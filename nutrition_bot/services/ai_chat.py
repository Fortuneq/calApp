import logging
from typing import List, Dict, Any
from openai import AsyncOpenAI
from config import config

logger = logging.getLogger(__name__)

client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)


async def ai_chat_response(
    user_message: str,
    meals_context: str,
    chat_history: List[Dict[str, str]]
) -> str:
    """
    Generate AI consultant response based on nutrition context

    Args:
        user_message: User's question
        meals_context: Recent meals history (formatted string)
        chat_history: Recent chat messages [{"role": "user|assistant", "content": "..."}]

    Returns:
        AI response text in markdown
    """
    try:
        logger.info(f"AI chat request: {user_message[:50]}...")

        # Build system prompt with nutrition context
        system_prompt = (
            "Ты AI-консультант по питанию.\n\n"
            "Контекст питания пользователя за последние 7 дней:\n"
            f"{meals_context}\n\n"
            "Твоя задача:\n"
            "- Анализировать питание пользователя\n"
            "- Давать рекомендации по КБЖУ\n"
            "- Отвечать на вопросы о здоровом питании\n"
            "- Быть дружелюбным и мотивирующим\n"
            "- Использовать markdown для форматирования\n"
            "- Отвечать кратко и по делу\n\n"
            "Если контекст питания пуст, предложи начать отслеживать приёмы пищи."
        )

        # Build messages
        messages = [{"role": "system", "content": system_prompt}]

        # Add chat history (last 10 messages)
        for msg in chat_history[-10:]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })

        # Call GPT-4
        response = await client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=messages,
            max_tokens=1000,
            temperature=0.7
        )

        assistant_message = response.choices[0].message.content
        logger.info(f"AI chat response generated ({len(assistant_message)} chars)")

        return assistant_message

    except Exception as e:
        logger.error(f"AI chat error: {e}", exc_info=True)
        return (
            "Извините, произошла ошибка при обработке вашего запроса. "
            "Попробуйте позже или переформулируйте вопрос."
        )


async def test_ai_chat() -> bool:
    """Test AI chat API connection"""
    try:
        result = await ai_chat_response(
            user_message="Привет!",
            meals_context="Нет данных о питании",
            chat_history=[]
        )
        logger.info(f"AI chat test result: {result[:100]}...")
        return len(result) > 0
    except Exception as e:
        logger.error(f"AI chat test failed: {e}")
        return False
