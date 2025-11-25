import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Application configuration"""

    # Telegram
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")

    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = "gpt-4o-latest"
    OPENAI_VISION_MODEL: str = "gpt-4o-latest"

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:pass@localhost:5432/nutrition_bot"
    )

    # Settings
    TIMEZONE: str = "Europe/Moscow"
    DIGEST_TIME: str = "21:00"  # MSK
    USER_CHAT_ID: str = os.getenv("USER_CHAT_ID", "***REMOVED***")

    # Rate limits
    THROTTLE_TIME: float = 0.5  # seconds

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    def validate(self) -> None:
        """Validate required configuration"""
        if not self.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")
        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")


config = Config()
