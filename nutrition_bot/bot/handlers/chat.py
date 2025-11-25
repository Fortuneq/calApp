"""
AI consultant handler for text messages in Telegram Nutrition Bot
"""
import logging
import uuid
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message
from aiogram.enums import ChatAction

from services.ai_chat import ai_chat_response
from database.crud import get_meals_last_week, save_chat_log, get_chat_logs
from utils.time import format_datetime_msk

logger = logging.getLogger(__name__)

router = Router()


def format_meals_context(meals: list) -> str:
    """
    Format meals history for AI context

    Args:
        meals: List of Meal objects

    Returns:
        Formatted string with meals history
    """
    if not meals:
        return "Нет данных о питании за последние 7 дней."

    lines = ["Приёмы пищи за последние 7 дней:"]

    for meal in meals:
        time_str = format_datetime_msk(meal.eaten_at)
        lines.append(
            f"\n{time_str}: {meal.dish} ({meal.grams}г) - "
            f"{meal.kcal} ккал (Б: {meal.prot}г, Ж: {meal.fat}г, У: {meal.carb}г)"
        )

    return "\n".join(lines)


@router.message(F.text & ~F.text.startswith("/"))
async def handle_text_message(message: Message):
    """
    Handle text messages (AI consultant)

    Flow:
    1. Get meals history for last 7 days
    2. Get chat logs for context
    3. Call AI chat service
    4. Save user message and assistant response to chat logs
    5. Send response to user
    """
    try:
        chat_id = str(message.chat.id)
        user_message = message.text.strip()
        user_info = f"@{message.from_user.username}" if message.from_user.username else str(message.from_user.id)

        # Ignore empty messages
        if not user_message:
            return

        logger.info(f"Text message from {user_info}: {user_message[:100]}...")

        # Show typing action
        await message.bot.send_chat_action(
            chat_id=message.chat.id,
            action=ChatAction.TYPING
        )

        # Generate session ID (use date as session key to separate by days)
        session_id = f"session_{datetime.now().strftime('%Y%m%d')}"

        try:
            # Get meals history for last 7 days
            meals = await get_meals_last_week(chat_id)
            meals_context = format_meals_context(meals)

            logger.debug(f"Retrieved {len(meals)} meals for context")

            # Get chat history
            chat_history = await get_chat_logs(
                chat_id=chat_id,
                session_id=session_id,
                limit=10
            )

            logger.debug(f"Retrieved {len(chat_history)} chat messages for context")

            # Call AI chat service
            assistant_response = await ai_chat_response(
                user_message=user_message,
                meals_context=meals_context,
                chat_history=chat_history
            )

            logger.info(f"AI response generated ({len(assistant_response)} chars)")

            # Save user message to chat logs
            await save_chat_log(
                chat_id=chat_id,
                session_id=session_id,
                role="user",
                content=user_message,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                metadata={
                    "message_id": message.message_id,
                    "date": message.date.isoformat() if message.date else None
                }
            )

            # Save assistant response to chat logs
            await save_chat_log(
                chat_id=chat_id,
                session_id=session_id,
                role="assistant",
                content=assistant_response,
                metadata={
                    "model": "gpt-4o-latest",
                    "meals_count": len(meals)
                }
            )

            logger.info(f"Chat logs saved for session {session_id}")

            # Send response to user
            await message.answer(
                text=assistant_response,
                parse_mode="Markdown"
            )

        except Exception as e:
            logger.error(f"Error in AI chat processing: {e}", exc_info=True)

            # Send error message
            await message.answer(
                "Извините, произошла ошибка при обработке вашего сообщения. "
                "Попробуйте переформулировать вопрос или попробуйте позже."
            )

    except Exception as e:
        logger.error(f"Error in text message handler: {e}", exc_info=True)
        try:
            await message.answer(
                "Произошла ошибка. Попробуйте ещё раз."
            )
        except:
            pass
