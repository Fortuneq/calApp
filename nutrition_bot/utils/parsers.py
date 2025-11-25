import re
from typing import Optional, Tuple
from datetime import datetime
from utils.time import parse_time_msk, now_msk


def parse_manual_entry(text: str) -> Optional[Tuple[str, int, Optional[datetime]]]:
    """
    Parse manual entry command text

    Format: /v блюдо граммы [время]

    Examples:
        "/v яблоко 150" -> ("яблоко", 150, None)
        "/v греча 200 18:30" -> ("греча", 200, datetime(...))
        "/v курица 180г 12:00" -> ("курица", 180, datetime(...))

    Args:
        text: Command text

    Returns:
        Tuple of (dish, grams, eaten_at) or None if parsing failed
    """
    try:
        # Remove /v command
        text = text.strip()
        if not text.startswith("/v"):
            return None

        parts = text[2:].strip().split()

        if len(parts) < 2:
            return None

        # Extract dish name (first part)
        dish = parts[0].strip()

        # Extract grams (second part, may contain 'г' suffix)
        grams_str = parts[1].strip()
        grams_match = re.search(r'(\d+)', grams_str)
        if not grams_match:
            return None
        grams = int(grams_match.group(1))

        # Extract time (optional third part)
        eaten_at = None
        if len(parts) >= 3:
            time_str = parts[2].strip()
            eaten_at = parse_time_msk(time_str)

        # Use current time if not specified
        if eaten_at is None:
            eaten_at = now_msk()

        return dish, grams, eaten_at

    except (ValueError, AttributeError, IndexError):
        return None


def extract_grams(text: str) -> Optional[int]:
    """
    Extract grams from text

    Examples:
        "150" -> 150
        "200г" -> 200
        "180 г" -> 180

    Args:
        text: Text containing grams

    Returns:
        Integer grams or None
    """
    try:
        match = re.search(r'(\d+)\s*г?', text.strip())
        if match:
            return int(match.group(1))
        return None
    except (ValueError, AttributeError):
        return None


def validate_grams(grams: int) -> bool:
    """
    Validate grams value

    Args:
        grams: Grams value

    Returns:
        True if valid (1-5000g), False otherwise
    """
    return 1 <= grams <= 5000


def sanitize_dish_name(dish: str) -> str:
    """
    Sanitize dish name

    Args:
        dish: Raw dish name

    Returns:
        Cleaned dish name
    """
    # Remove extra whitespace
    dish = " ".join(dish.split())

    # Capitalize first letter
    dish = dish.strip().lower()
    if dish:
        dish = dish[0].upper() + dish[1:]

    return dish[:255]  # Max length from DB schema
