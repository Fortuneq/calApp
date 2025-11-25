import re
from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo
from typing import Optional
from config import config


def now_msk() -> datetime:
    """Get current datetime in Moscow timezone"""
    return datetime.now(ZoneInfo(config.TIMEZONE))


def today_msk() -> date:
    """Get current date in Moscow timezone"""
    return now_msk().date()


def parse_time_msk(time_str: str) -> Optional[datetime]:
    """
    Parse time string to datetime in Moscow timezone

    Args:
        time_str: Time string in format "HH:MM" or "H:MM"

    Returns:
        datetime object or None if parsing failed

    Examples:
        "18:30" -> datetime(today, 18, 30, tzinfo=MSK)
        "9:15" -> datetime(today, 9, 15, tzinfo=MSK)
    """
    try:
        # Match HH:MM or H:MM
        match = re.match(r'^(\d{1,2}):(\d{2})$', time_str.strip())
        if not match:
            return None

        hour = int(match.group(1))
        minute = int(match.group(2))

        # Validate ranges
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            return None

        # Create datetime for today
        today = today_msk()
        time_obj = time(hour, minute)

        return datetime.combine(today, time_obj, tzinfo=ZoneInfo(config.TIMEZONE))

    except (ValueError, AttributeError):
        return None


def format_datetime_msk(dt: datetime) -> str:
    """
    Format datetime to string in Moscow timezone

    Args:
        dt: datetime object

    Returns:
        Formatted string "DD.MM.YYYY HH:MM"
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo(config.TIMEZONE))
    else:
        dt = dt.astimezone(ZoneInfo(config.TIMEZONE))

    return dt.strftime("%d.%m.%Y %H:%M")


def get_date_range_last_week() -> tuple[datetime, datetime]:
    """
    Get datetime range for last 7 days in Moscow timezone

    Returns:
        Tuple of (start_datetime, end_datetime)
    """
    end = now_msk()
    start = end - timedelta(days=7)

    return start, end


def get_start_of_day(day: Optional[date] = None) -> datetime:
    """
    Get start of day (00:00:00) in Moscow timezone

    Args:
        day: Date object (default: today)

    Returns:
        datetime at 00:00:00
    """
    if day is None:
        day = today_msk()

    return datetime.combine(day, time(0, 0, 0), tzinfo=ZoneInfo(config.TIMEZONE))


def get_end_of_day(day: Optional[date] = None) -> datetime:
    """
    Get end of day (23:59:59) in Moscow timezone

    Args:
        day: Date object (default: today)

    Returns:
        datetime at 23:59:59
    """
    if day is None:
        day = today_msk()

    return datetime.combine(day, time(23, 59, 59), tzinfo=ZoneInfo(config.TIMEZONE))
