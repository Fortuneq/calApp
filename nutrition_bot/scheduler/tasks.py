import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from aiogram import Bot

from config import config
from database.crud import get_meals_for_date, upsert_digest
from services.digest import generate_digest_text
from utils.time import today_msk

logger = logging.getLogger(__name__)

# Create scheduler instance
scheduler = AsyncIOScheduler(timezone=config.TIMEZONE)


async def send_daily_digest(bot: Bot):
    """
    Send daily digest to user at 21:00 MSK

    Args:
        bot: Telegram Bot instance
    """
    try:
        today = today_msk()
        chat_id = config.USER_CHAT_ID

        logger.info(f"Starting daily digest generation for {today}")

        # Get meals for today
        meals = await get_meals_for_date(chat_id, today)

        if not meals:
            logger.info(f"No meals found for {chat_id} on {today}")
            return

        # Calculate totals
        total_kcal = sum(m.kcal for m in meals)
        total_prot = sum(m.prot for m in meals)
        total_fat = sum(m.fat for m in meals)
        total_carb = sum(m.carb for m in meals)

        logger.info(
            f"Digest totals: {total_kcal} kcal, "
            f"P:{total_prot}g F:{total_fat}g C:{total_carb}g"
        )

        # Generate digest text via GPT-4
        summary_md = await generate_digest_text(
            meals=meals,
            total_kcal=total_kcal,
            total_prot=total_prot,
            total_fat=total_fat,
            total_carb=total_carb
        )

        # Send to Telegram
        msg = await bot.send_message(
            chat_id=chat_id,
            text=summary_md,
            parse_mode="Markdown"
        )

        # Save digest to database
        await upsert_digest(
            chat_id=chat_id,
            for_date=today,
            kcal=total_kcal,
            prot=total_prot,
            fat=total_fat,
            carb=total_carb,
            meals_json=[
                {
                    "dish": m.dish,
                    "grams": m.grams,
                    "kcal": m.kcal,
                    "prot": m.prot,
                    "fat": m.fat,
                    "carb": m.carb,
                    "time": m.eaten_at.isoformat()
                }
                for m in meals
            ],
            summary_md=summary_md,
            msg_id=msg.message_id
        )

        logger.info(f"Daily digest sent successfully to {chat_id}")

    except Exception as e:
        logger.error(f"Error sending daily digest: {e}", exc_info=True)


def start_scheduler(bot: Bot):
    """
    Start the scheduler for daily digests

    Args:
        bot: Telegram Bot instance
    """
    # Parse digest time (format: "HH:MM")
    hour, minute = map(int, config.DIGEST_TIME.split(":"))

    # Add daily digest job
    scheduler.add_job(
        send_daily_digest,
        trigger=CronTrigger(
            hour=hour,
            minute=minute,
            timezone=config.TIMEZONE
        ),
        args=[bot],
        id="daily_digest",
        name="Daily Nutrition Digest",
        replace_existing=True,
        misfire_grace_time=300  # 5 minutes grace period
    )

    scheduler.start()
    logger.info(
        f"Scheduler started - Daily digest at {config.DIGEST_TIME} {config.TIMEZONE}"
    )


def stop_scheduler():
    """Stop the scheduler gracefully"""
    if scheduler.running:
        scheduler.shutdown(wait=True)
        logger.info("Scheduler stopped")


async def trigger_digest_now(bot: Bot):
    """
    Manually trigger digest generation (for testing)

    Args:
        bot: Telegram Bot instance
    """
    logger.info("Manually triggering digest")
    await send_daily_digest(bot)
