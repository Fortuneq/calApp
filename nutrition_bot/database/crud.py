import json
import logging
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Meal, MealDraft, Digest, ChatLog
from database.connection import AsyncSessionLocal

logger = logging.getLogger(__name__)


# ==================== Meals ====================

async def create_meal(
    chat_id: str,
    dish: str,
    grams: int,
    kcal: int,
    prot: int,
    fat: int,
    carb: int,
    eaten_at: datetime
) -> Meal:
    """Create new meal record"""
    async with AsyncSessionLocal() as session:
        meal = Meal(
            chat_id=chat_id,
            dish=dish,
            grams=grams,
            kcal=kcal,
            prot=prot,
            fat=fat,
            carb=carb,
            eaten_at=eaten_at,
            deleted=False
        )
        session.add(meal)
        await session.commit()
        await session.refresh(meal)
        logger.info(f"Created meal: {meal.dish} ({meal.id})")
        return meal


async def get_meal_by_id(meal_id: int) -> Optional[Meal]:
    """Get meal by ID"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Meal).where(Meal.id == meal_id)
        )
        return result.scalar_one_or_none()


async def soft_delete_meal(meal_id: int) -> bool:
    """Soft delete meal (set deleted=True)"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Meal).where(Meal.id == meal_id)
        )
        meal = result.scalar_one_or_none()

        if meal:
            meal.deleted = True
            await session.commit()
            logger.info(f"Soft deleted meal: {meal.id}")
            return True

        return False


async def get_meals_for_date(chat_id: str, date: date) -> List[Meal]:
    """Get all non-deleted meals for specific date"""
    async with AsyncSessionLocal() as session:
        # Get start and end of day
        from utils.time import get_start_of_day, get_end_of_day
        start = get_start_of_day(date)
        end = get_end_of_day(date)

        result = await session.execute(
            select(Meal)
            .where(
                and_(
                    Meal.chat_id == chat_id,
                    Meal.eaten_at >= start,
                    Meal.eaten_at <= end,
                    Meal.deleted == False
                )
            )
            .order_by(Meal.eaten_at)
        )
        return list(result.scalars().all())


async def get_meals_last_week(chat_id: str) -> List[Meal]:
    """Get all non-deleted meals for last 7 days"""
    async with AsyncSessionLocal() as session:
        from utils.time import get_date_range_last_week
        start, end = get_date_range_last_week()

        result = await session.execute(
            select(Meal)
            .where(
                and_(
                    Meal.chat_id == chat_id,
                    Meal.eaten_at >= start,
                    Meal.eaten_at <= end,
                    Meal.deleted == False
                )
            )
            .order_by(Meal.eaten_at.desc())
        )
        return list(result.scalars().all())


# ==================== Meals Draft ====================

async def create_draft(
    chat_id: str,
    message_id: int,
    photo_file_id: Optional[str],
    candidates: List[Dict[str, Any]],
    grams_pred: int,
    status: str
) -> MealDraft:
    """Create new draft record"""
    async with AsyncSessionLocal() as session:
        draft = MealDraft(
            chat_id=chat_id,
            message_id=message_id,
            photo_file_id=photo_file_id,
            candidates=candidates,
            grams_pred=grams_pred,
            chosen_name=None,
            status=status
        )
        session.add(draft)
        await session.commit()
        await session.refresh(draft)
        logger.info(f"Created draft: {draft.id} (status: {status})")
        return draft


async def get_draft(chat_id: str, message_id: int) -> Optional[MealDraft]:
    """Get draft by chat_id and message_id"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(MealDraft).where(
                and_(
                    MealDraft.chat_id == chat_id,
                    MealDraft.message_id == message_id
                )
            )
        )
        return result.scalar_one_or_none()


async def get_draft_by_id(draft_id: int) -> Optional[MealDraft]:
    """Get draft by ID"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(MealDraft).where(MealDraft.id == draft_id)
        )
        return result.scalar_one_or_none()


async def update_draft(
    draft_id: int,
    status: Optional[str] = None,
    chosen_name: Optional[str] = None,
    grams_pred: Optional[int] = None
) -> bool:
    """Update draft record"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(MealDraft).where(MealDraft.id == draft_id)
        )
        draft = result.scalar_one_or_none()

        if draft:
            if status is not None:
                draft.status = status
            if chosen_name is not None:
                draft.chosen_name = chosen_name
            if grams_pred is not None:
                draft.grams_pred = grams_pred

            draft.updated_at = datetime.utcnow()
            await session.commit()
            logger.info(f"Updated draft: {draft.id} (status: {draft.status})")
            return True

        return False


def safe_parse_candidates(candidates: Any) -> List[Dict[str, Any]]:
    """Safely parse candidates JSON (handles double serialization)"""
    if isinstance(candidates, list):
        return candidates

    if isinstance(candidates, str):
        try:
            # First parse
            result = json.loads(candidates)

            # Second parse if still string
            if isinstance(result, str):
                result = json.loads(result)

            return result if isinstance(result, list) else []
        except json.JSONDecodeError:
            logger.error(f"Failed to parse candidates: {candidates}")
            return []

    return []


# ==================== Digest ====================

async def upsert_digest(
    chat_id: str,
    for_date: date,
    kcal: int,
    prot: int,
    fat: int,
    carb: int,
    meals_json: List[Dict[str, Any]],
    summary_md: str,
    msg_id: Optional[int] = None
) -> Digest:
    """Create or update digest record"""
    async with AsyncSessionLocal() as session:
        # Try to find existing digest
        result = await session.execute(
            select(Digest).where(
                and_(
                    Digest.chat_id == chat_id,
                    Digest.for_date == for_date
                )
            )
        )
        digest = result.scalar_one_or_none()

        if digest:
            # Update existing
            digest.kcal = kcal
            digest.prot = prot
            digest.fat = fat
            digest.carb = carb
            digest.meals_json = meals_json
            digest.summary_md = summary_md
            if msg_id is not None:
                digest.msg_id = msg_id
            logger.info(f"Updated digest: {digest.id}")
        else:
            # Create new
            digest = Digest(
                chat_id=chat_id,
                for_date=for_date,
                kcal=kcal,
                prot=prot,
                fat=fat,
                carb=carb,
                meals_json=meals_json,
                summary_md=summary_md,
                msg_id=msg_id
            )
            session.add(digest)
            logger.info(f"Created digest for {for_date}")

        await session.commit()
        await session.refresh(digest)
        return digest


async def get_digest(chat_id: str, for_date: date) -> Optional[Digest]:
    """Get digest for specific date"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Digest).where(
                and_(
                    Digest.chat_id == chat_id,
                    Digest.for_date == for_date
                )
            )
        )
        return result.scalar_one_or_none()


# ==================== Chat Logs ====================

async def save_chat_log(
    chat_id: str,
    session_id: str,
    role: str,
    content: str,
    username: Optional[str] = None,
    first_name: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> ChatLog:
    """Save chat log entry"""
    async with AsyncSessionLocal() as session:
        log = ChatLog(
            chat_id=chat_id,
            session_id=session_id,
            role=role,
            content=content,
            username=username,
            first_name=first_name,
            metadata=metadata
        )
        session.add(log)
        await session.commit()
        await session.refresh(log)
        return log


async def get_chat_logs(
    chat_id: str,
    session_id: str,
    limit: int = 10
) -> List[Dict[str, str]]:
    """
    Get recent chat logs for AI context

    Returns:
        List of {"role": "user|assistant", "content": "..."}
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(ChatLog)
            .where(
                and_(
                    ChatLog.chat_id == chat_id,
                    ChatLog.session_id == session_id,
                    ChatLog.role.in_(['user', 'assistant'])
                )
            )
            .order_by(ChatLog.created_at.desc())
            .limit(limit)
        )
        logs = list(result.scalars().all())

        # Reverse to get chronological order
        logs.reverse()

        return [
            {"role": log.role, "content": log.content}
            for log in logs
        ]


# ==================== Utility ====================

async def get_all_users() -> List[str]:
    """Get list of all unique chat_ids"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Meal.chat_id).distinct()
        )
        return [row[0] for row in result.all()]
