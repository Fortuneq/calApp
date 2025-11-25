import logging
from typing import List
from datetime import datetime
from openai import AsyncOpenAI
from config import config
from database.models import Meal

logger = logging.getLogger(__name__)

client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)


async def generate_digest_text(
    meals: List[Meal],
    total_kcal: int,
    total_prot: int,
    total_fat: int,
    total_carb: int
) -> str:
    """
    Generate daily digest summary using GPT-4

    Args:
        meals: List of Meal objects for the day
        total_kcal: Total calories
        total_prot: Total protein (g)
        total_fat: Total fat (g)
        total_carb: Total carbs (g)

    Returns:
        Markdown formatted digest text
    """
    try:
        logger.info(f"Generating digest for {len(meals)} meals")

        # Format meals list
        meals_text = "\n".join([
            f"- {m.eaten_at.strftime('%H:%M')} - {m.dish} ({m.grams}г): "
            f"{m.kcal} ккал, Б{m.prot} Ж{m.fat} У{m.carb}"
            for m in meals
        ])

        # Build prompt
        prompt = (
            f"Проанализируй питание пользователя за день:\n\n"
            f"**Приёмы пищи:**\n{meals_text}\n\n"
            f"**Итого за день:**\n"
            f"- Калории: {total_kcal} ккал\n"
            f"- Белки: {total_prot} г\n"
            f"- Жиры: {total_fat} г\n"
            f"- Углеводы: {total_carb} г\n\n"
            f"Создай краткий дайджест (2-3 абзаца) с:\n"
            f"1. Общей оценкой питания за день\n"
            f"2. Рекомендациями по балансу КБЖУ\n"
            f"3. Позитивной мотивацией\n\n"
            f"Используй markdown для форматирования. Будь кратким и дружелюбным."
        )

        response = await client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты AI-консультант по питанию. "
                        "Создаёшь ежедневные дайджесты питания. "
                        "Стиль: дружелюбный, мотивирующий, экспертный."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=800,
            temperature=0.7
        )

        digest_text = response.choices[0].message.content

        # Add header
        today = datetime.now().strftime('%d.%m.%Y')
        full_digest = (
            f"📊 **Дайджест за {today}**\n\n"
            f"**КБЖУ:** {total_kcal} / {total_prot} / {total_fat} / {total_carb}\n\n"
            f"{digest_text}"
        )

        logger.info(f"Digest generated ({len(full_digest)} chars)")
        return full_digest

    except Exception as e:
        logger.error(f"Digest generation error: {e}", exc_info=True)
        # Fallback digest
        today = datetime.now().strftime('%d.%m.%Y')
        return (
            f"📊 **Дайджест за {today}**\n\n"
            f"**КБЖУ:** {total_kcal} / {total_prot} / {total_fat} / {total_carb}\n\n"
            f"Сегодня вы употребили {len(meals)} приёмов пищи. "
            f"Продолжайте отслеживать своё питание!"
        )
