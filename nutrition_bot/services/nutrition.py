import json
import logging
from typing import Dict, Any
from openai import AsyncOpenAI
from config import config

logger = logging.getLogger(__name__)

client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)


async def calculate_nutrition(dish: str, grams: int) -> Dict[str, Any]:
    """
    Calculate nutrition (KBJU) using GPT-4

    Args:
        dish: Dish name in Russian
        grams: Weight in grams

    Returns:
        {
            "dish": "яблоко",
            "kcal": 52,
            "prot": 0,
            "fat": 0,
            "carb": 14
        }
    """
    try:
        logger.info(f"Calculating nutrition for: {dish} ({grams}g)")

        response = await client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты нутри-калькулятор.\n"
                        "На вход получаешь JSON {\"dish\":\"название_блюда\", \"grams\":масса_в_граммах}.\n\n"
                        "Отвечай строго JSON одной строкой:\n"
                        "{\n"
                        ' "dish":"название блюда на русском",\n'
                        ' "kcal":калории_целое_число,\n'
                        ' "prot":белки_граммы_целое_число,\n'
                        ' "fat":жиры_граммы_целое_число,\n'
                        ' "carb":углеводы_граммы_целое_число\n'
                        "}\n\n"
                        "Требования:\n"
                        "- Все значения целые числа\n"
                        "- Название блюда на русском языке\n"
                        "- Расчёт КБЖУ для указанной массы\n"
                        "- Без пояснений, без markdown разметки\n"
                        "- Только чистый JSON"
                    )
                },
                {
                    "role": "user",
                    "content": json.dumps({"dish": dish, "grams": grams}, ensure_ascii=False)
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=200,
            temperature=0.1
        )

        content = response.choices[0].message.content
        logger.debug(f"Nutrition API response: {content}")

        # Parse JSON
        result = json.loads(content)

        # Validate response
        required_fields = ["dish", "kcal", "prot", "fat", "carb"]
        if not all(field in result for field in required_fields):
            raise ValueError(f"Missing required fields in response: {result}")

        # Convert to integers
        result["kcal"] = int(result["kcal"])
        result["prot"] = int(result["prot"])
        result["fat"] = int(result["fat"])
        result["carb"] = int(result["carb"])

        logger.info(f"Nutrition calculated: {result}")
        return result

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}, content: {content}")
        # Fallback values
        return {
            "dish": dish,
            "kcal": 0,
            "prot": 0,
            "fat": 0,
            "carb": 0
        }
    except Exception as e:
        logger.error(f"Nutrition API error: {e}", exc_info=True)
        # Fallback values
        return {
            "dish": dish,
            "kcal": 0,
            "prot": 0,
            "fat": 0,
            "carb": 0
        }


async def test_nutrition_api() -> bool:
    """Test Nutrition API connection"""
    try:
        result = await calculate_nutrition("яблоко", 100)
        logger.info(f"Nutrition API test result: {result}")
        return result["kcal"] > 0
    except Exception as e:
        logger.error(f"Nutrition API test failed: {e}")
        return False
