"""
Start command handler for Telegram Nutrition Bot
"""
import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """
    Handle /start command

    Sends welcome message with bot features and usage instructions
    """
    try:
        user_name = message.from_user.first_name or "пользователь"

        welcome_text = (
            f"Привет, {user_name}!\n\n"
            "Я - бот для учёта питания с искусственным интеллектом.\n\n"
            "Что я умею:\n"
            "  Распознаю еду на фото и считаю КБЖУ\n"
            "  Помогаю вести дневник питания\n"
            "  Консультирую по вопросам питания\n"
            "  Создаю ежедневные отчёты\n\n"
            "Как пользоваться:\n\n"
            "  Просто отправь мне фото еды - я распознаю блюдо, определю вес "
            "и рассчитаю калории и БЖУ.\n\n"
            "  /v блюдо граммы [время] - добавить запись вручную\n"
            "  Например: /v яблоко 150 или /v греча 200 18:30\n\n"
            "  Напиши любое сообщение - задай вопрос о питании, "
            "попроси совет или анализ твоего рациона.\n\n"
            "  В 21:00 (МСК) я пришлю тебе дневной отчёт с рекомендациями.\n\n"
            "Начнём? Отправь мне фото своего завтрака, обеда или ужина!"
        )

        await message.answer(welcome_text)

        logger.info(
            f"Start command from user {message.from_user.id} "
            f"(@{message.from_user.username})"
        )

    except Exception as e:
        logger.error(f"Error in start handler: {e}", exc_info=True)
        await message.answer(
            "Произошла ошибка при обработке команды. Попробуйте ещё раз."
        )
