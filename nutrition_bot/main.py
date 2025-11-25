#!/usr/bin/env python3
"""
Telegram Nutrition Tracking Bot

Main entry point for the application
"""

import asyncio
import logging
import signal
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import config
from database.connection import init_db, close_db
from utils.logger import setup_logger
from scheduler.tasks import start_scheduler, stop_scheduler

# Import all routers
from bot.handlers import (
    start_router,
    photo_router,
    callbacks_router,
    manual_router,
    chat_router
)

logger = logging.getLogger(__name__)

# Global variables for graceful shutdown
bot_instance = None
dispatcher_instance = None


async def on_startup():
    """Execute on bot startup"""
    logger.info("=" * 60)
    logger.info("Starting Telegram Nutrition Bot")
    logger.info("=" * 60)

    # Validate configuration
    try:
        config.validate()
        logger.info("Configuration validated successfully")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)

    # Initialize database
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}", exc_info=True)
        sys.exit(1)

    # Test OpenAI API connections (optional)
    try:
        from services import test_vision_api, test_nutrition_api, test_ai_chat

        logger.info("Testing OpenAI API connections...")
        # Uncomment to test APIs on startup
        # vision_ok = await test_vision_api()
        # nutrition_ok = await test_nutrition_api()
        # chat_ok = await test_ai_chat()
        # logger.info(f"API tests: Vision={vision_ok}, Nutrition={nutrition_ok}, Chat={chat_ok}")
    except Exception as e:
        logger.warning(f"API test skipped: {e}")

    logger.info("Bot startup completed successfully")


async def on_shutdown():
    """Execute on bot shutdown"""
    logger.info("=" * 60)
    logger.info("Shutting down Telegram Nutrition Bot")
    logger.info("=" * 60)

    # Stop scheduler
    try:
        stop_scheduler()
        logger.info("Scheduler stopped")
    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}")

    # Close database connections
    try:
        await close_db()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database: {e}")

    logger.info("Bot shutdown completed")


def setup_handlers(dp: Dispatcher):
    """
    Register all handlers with the dispatcher

    IMPORTANT: Order matters! chat_router must be last
    because it catches all text messages.
    """
    dp.include_router(start_router)
    dp.include_router(manual_router)
    dp.include_router(photo_router)
    dp.include_router(callbacks_router)
    dp.include_router(chat_router)  # Must be last!

    logger.info("All handlers registered successfully")


async def main():
    """Main bot function"""
    global bot_instance, dispatcher_instance

    # Setup logging
    setup_logger(config.LOG_LEVEL)

    # Create bot instance
    bot_instance = Bot(
        token=config.TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.MARKDOWN
        )
    )

    # Create dispatcher
    dispatcher_instance = Dispatcher()

    # Register handlers
    setup_handlers(dispatcher_instance)

    # Startup actions
    await on_startup()

    # Start scheduler
    try:
        start_scheduler(bot_instance)
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}", exc_info=True)

    # Start polling
    try:
        logger.info("Starting bot polling...")
        await dispatcher_instance.start_polling(
            bot_instance,
            allowed_updates=["message", "callback_query"]
        )
    except Exception as e:
        logger.error(f"Polling error: {e}", exc_info=True)
    finally:
        await on_shutdown()


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    # Cancel the running event loop
    for task in asyncio.all_tasks():
        task.cancel()


if __name__ == "__main__":
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Run the bot
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user (KeyboardInterrupt)")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
