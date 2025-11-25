"""
Photo message handler with FSM logic for Telegram Nutrition Bot
"""
import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, BufferedInputFile
from aiogram.exceptions import TelegramAPIError

from services.vision import analyze_food_photo
from database.crud import create_draft
from bot.keyboards.inline import dish_confirmation_keyboard

logger = logging.getLogger(__name__)

router = Router()


@router.message(F.photo)
async def handle_photo(message: Message, bot: Bot):
    """
    Handle incoming photo messages

    FSM Flow:
    1. Download photo from Telegram
    2. Analyze with Vision API
    3. Create draft with status="await_dish"
    4. Show dish confirmation keyboard
    """
    try:
        chat_id = str(message.chat.id)
        user_info = f"@{message.from_user.username}" if message.from_user.username else str(message.from_user.id)

        logger.info(f"Received photo from {user_info}")

        # Send processing message
        processing_msg = await message.answer("Анализирую фото...")

        # Get the largest photo (last in array)
        photo = message.photo[-1]
        photo_file_id = photo.file_id

        try:
            # Download photo
            file = await bot.get_file(photo_file_id)
            photo_bytes = await bot.download_file(file.file_path)

            logger.debug(f"Downloaded photo: {len(photo_bytes.read())} bytes")
            photo_bytes.seek(0)  # Reset stream position

            # Analyze with Vision API
            candidates = await analyze_food_photo(photo_bytes.read())

            if not candidates or len(candidates) == 0:
                await processing_msg.edit_text(
                    "Не удалось распознать блюдо на фото. "
                    "Попробуйте сделать фото получше или используйте команду /v для ручного ввода."
                )
                logger.warning(f"No candidates returned for photo from {user_info}")
                return

            # Get top candidate
            top_candidate = candidates[0]
            dish_name = top_candidate.get("dish", "неизвестное блюдо")
            predicted_grams = top_candidate.get("grams", 100)
            confidence = top_candidate.get("confidence", 0.0)

            logger.info(
                f"Vision API result: {dish_name} ({predicted_grams}g, "
                f"confidence: {confidence:.2f})"
            )

            # Create draft in database
            draft = await create_draft(
                chat_id=chat_id,
                message_id=message.message_id,
                photo_file_id=photo_file_id,
                candidates=candidates,
                grams_pred=predicted_grams,
                status="await_dish"
            )

            logger.info(f"Created draft {draft.id} for message {message.message_id}")

            # Show dish confirmation
            confirmation_text = (
                f"Распознал:\n"
                f"  {dish_name}\n"
                f"  ~{predicted_grams} г\n\n"
                f"Всё верно?"
            )

            await processing_msg.edit_text(
                text=confirmation_text,
                reply_markup=dish_confirmation_keyboard(message.message_id)
            )

        except TelegramAPIError as e:
            logger.error(f"Telegram API error: {e}", exc_info=True)
            await processing_msg.edit_text(
                "Ошибка при загрузке фото. Попробуйте ещё раз."
            )

        except Exception as e:
            logger.error(f"Error processing photo: {e}", exc_info=True)
            await processing_msg.edit_text(
                "Произошла ошибка при анализе фото. Попробуйте ещё раз или "
                "используйте команду /v для ручного ввода."
            )

    except Exception as e:
        logger.error(f"Error in photo handler: {e}", exc_info=True)
        try:
            await message.answer(
                "Произошла ошибка при обработке фото. Попробуйте ещё раз."
            )
        except:
            pass
