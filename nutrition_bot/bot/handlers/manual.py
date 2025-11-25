"""
Manual entry handler for /v command in Telegram Nutrition Bot
"""
import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from utils.parsers import parse_manual_entry, validate_grams, sanitize_dish_name
from services.nutrition import calculate_nutrition
from database.crud import create_meal
from bot.keyboards.inline import cancel_meal_keyboard
from utils.time import now_msk, format_datetime_msk

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("v"))
async def cmd_manual_entry(message: Message):
    """
    Handle manual entry command /v

    Format: /v блюдо граммы [время]

    Examples:
        /v яблоко 150
        /v греча 200 18:30
        /v курица 180г 12:00
    """
    try:
        chat_id = str(message.chat.id)
        user_info = f"@{message.from_user.username}" if message.from_user.username else str(message.from_user.id)

        logger.info(f"Manual entry from {user_info}: {message.text}")

        # Parse command
        parsed = parse_manual_entry(message.text)

        if parsed is None:
            await message.answer(
                "Неверный формат команды.\n\n"
                "Используйте:\n"
                "/v блюдо граммы [время]\n\n"
                "Примеры:\n"
                "  /v яблоко 150\n"
                "  /v греча 200 18:30\n"
                "  /v курица 180г 12:00"
            )
            logger.warning(f"Failed to parse manual entry: {message.text}")
            return

        dish, grams, eaten_at = parsed

        # Validate grams
        if not validate_grams(grams):
            await message.answer(
                f"Неверный вес: {grams} г.\n"
                f"Вес должен быть от 1 до 5000 грамм."
            )
            logger.warning(f"Invalid grams value: {grams}")
            return

        # Sanitize dish name
        dish = sanitize_dish_name(dish)

        # Use current time if not specified
        if eaten_at is None:
            eaten_at = now_msk()

        logger.info(f"Parsed: dish={dish}, grams={grams}, eaten_at={eaten_at}")

        # Send calculating message
        calculating_msg = await message.answer("Рассчитываю КБЖУ...")

        try:
            # Calculate nutrition
            nutrition = await calculate_nutrition(dish, grams)

            dish_normalized = nutrition.get("dish", dish)
            kcal = nutrition.get("kcal", 0)
            prot = nutrition.get("prot", 0)
            fat = nutrition.get("fat", 0)
            carb = nutrition.get("carb", 0)

            logger.info(
                f"Nutrition calculated for {dish_normalized} ({grams}g): "
                f"{kcal} kcal, P:{prot} F:{fat} C:{carb}"
            )

            # Create meal in database
            meal = await create_meal(
                chat_id=chat_id,
                dish=dish_normalized,
                grams=grams,
                kcal=kcal,
                prot=prot,
                fat=fat,
                carb=carb,
                eaten_at=eaten_at
            )

            logger.info(f"Meal {meal.id} created successfully (manual entry)")

            # Show confirmation
            confirmation_text = (
                f"{dish_normalized} ({grams} г)\n\n"
                f"КБЖУ:\n"
                f"  Калории: {kcal} ккал\n"
                f"  Белки: {prot} г\n"
                f"  Жиры: {fat} г\n"
                f"  Углеводы: {carb} г\n\n"
                f"Время: {format_datetime_msk(eaten_at)}\n\n"
                f"Сохранено!"
            )

            await calculating_msg.edit_text(
                text=confirmation_text,
                reply_markup=cancel_meal_keyboard(meal.id)
            )

        except Exception as e:
            logger.error(f"Error calculating/saving meal: {e}", exc_info=True)
            await calculating_msg.edit_text(
                "Произошла ошибка при расчёте КБЖУ. Попробуйте ещё раз."
            )

    except Exception as e:
        logger.error(f"Error in manual entry handler: {e}", exc_info=True)
        try:
            await message.answer(
                "Произошла ошибка при обработке команды. Попробуйте ещё раз."
            )
        except:
            pass


@router.message(F.text.regexp(r"^/v\b"))
async def cmd_manual_entry_fallback(message: Message):
    """
    Fallback handler for /v command without proper arguments
    """
    await message.answer(
        "Неверный формат команды.\n\n"
        "Используйте:\n"
        "/v блюдо граммы [время]\n\n"
        "Примеры:\n"
        "  /v яблоко 150\n"
        "  /v греча 200 18:30\n"
        "  /v курица 180г 12:00"
    )
