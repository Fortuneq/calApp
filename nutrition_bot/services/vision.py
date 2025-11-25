import json
import base64
import logging
from typing import List, Dict, Any
from openai import AsyncOpenAI
from config import config

logger = logging.getLogger(__name__)

client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)


async def analyze_food_photo(photo_bytes: bytes) -> List[Dict[str, Any]]:
    """
    Analyze food photo using GPT-4 Vision API

    Args:
        photo_bytes: Image bytes

    Returns:
        List of dish candidates with structure:
        [
            {"dish": "греческий йогурт", "grams": 140, "confidence": 0.98},
            {"dish": "йогурт", "grams": 140, "confidence": 0.92},
            ...
        ]
    """
    try:
        # Encode image to base64
        base64_image = base64.b64encode(photo_bytes).decode('utf-8')

        logger.info("Sending photo to Vision API")

        response = await client.chat.completions.create(
            model=config.OPENAI_VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Ты пищевой классификатор.\n"
                                "Проанализируй изображение еды и верни JSON ТОЛЬКО на русском языке, без markdown разметки.\n\n"
                                "Формат ответа:\n"
                                "{\n"
                                '  "candidates": [\n'
                                '    {"dish": "название блюда", "grams": примерная_масса_в_граммах, "confidence": уверенность_от_0_до_1},\n'
                                "    ... (максимум 3 варианта)\n"
                                "  ]\n"
                                "}\n\n"
                                "Требования:\n"
                                "- Названия блюд на русском языке\n"
                                "- Масса в граммах (целое число)\n"
                                "- Уверенность от 0 до 1 (float)\n"
                                "- Отсортируй по убыванию уверенности\n"
                                "- Не используй markdown (```json), только чистый JSON"
                            )
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500,
            temperature=0.3
        )

        content = response.choices[0].message.content
        logger.debug(f"Vision API response: {content}")

        # Clean up markdown if present
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        # Parse JSON
        parsed = json.loads(content)

        candidates = parsed.get("candidates", [])

        if not candidates:
            logger.warning("No candidates returned from Vision API")
            return [{"dish": "неизвестное блюдо", "grams": 100, "confidence": 0.5}]

        logger.info(f"Vision API returned {len(candidates)} candidates")
        return candidates

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}, content: {content}")
        return [{"dish": "неизвестное блюдо", "grams": 100, "confidence": 0.5}]
    except Exception as e:
        logger.error(f"Vision API error: {e}", exc_info=True)
        return [{"dish": "ошибка распознавания", "grams": 100, "confidence": 0.0}]


async def test_vision_api() -> bool:
    """Test Vision API connection"""
    try:
        # Create a simple test image (1x1 white pixel)
        import io
        from PIL import Image

        img = Image.new('RGB', (1, 1), color='white')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)

        result = await analyze_food_photo(img_bytes.read())
        logger.info(f"Vision API test result: {result}")
        return True
    except Exception as e:
        logger.error(f"Vision API test failed: {e}")
        return False
