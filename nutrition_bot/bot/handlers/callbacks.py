"""
Callback query handlers for inline buttons in Telegram Nutrition Bot
"""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramAPIError

from database.crud import (
    get_draft,
    update_draft,
    create_meal,
    soft_delete_meal,
    get_meal_by_id,
    safe_parse_candidates
)
from services.nutrition import calculate_nutrition
from bot.keyboards.inline import (
    alternatives_keyboard,
    weight_selection_keyboard,
    cancel_meal_keyboard
)
from utils.time import now_msk, format_datetime_msk

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data.startswith("dish_yes_"))
async def callback_dish_yes(callback: CallbackQuery):
    """
    Handle dish confirmation: User confirmed the recognized dish

    Flow: await_dish -> await_weight
    """
    try:
        await callback.answer()

        # Extract message_id from callback data
        message_id = int(callback.data.split("_")[-1])
        chat_id = str(callback.message.chat.id)

        logger.info(f"Dish confirmed for message {message_id}")

        # Get draft from database
        draft = await get_draft(chat_id, message_id)

        if not draft:
            await callback.message.edit_text("Ошибка: данные не найдены.")
            logger.error(f"Draft not found for message {message_id}")
            return

        # Parse candidates
        candidates = safe_parse_candidates(draft.candidates)

        if not candidates or len(candidates) == 0:
            await callback.message.edit_text("Ошибка: не удалось получить данные блюда.")
            logger.error(f"No candidates in draft {draft.id}")
            return

        # Get top candidate
        top_candidate = candidates[0]
        chosen_dish = top_candidate.get("dish", "неизвестное блюдо")
        predicted_grams = draft.grams_pred or 100

        # Update draft: set chosen_name and status
        await update_draft(
            draft_id=draft.id,
            chosen_name=chosen_dish,
            status="await_weight"
        )

        logger.info(f"Draft {draft.id} updated: chosen_name={chosen_dish}, status=await_weight")

        # Show weight selection keyboard
        weight_text = (
            f"{chosen_dish}\n\n"
            f"Выберите вес:"
        )

        await callback.message.edit_text(
            text=weight_text,
            reply_markup=weight_selection_keyboard(message_id, predicted_grams)
        )

    except Exception as e:
        logger.error(f"Error in dish_yes callback: {e}", exc_info=True)
        try:
            await callback.message.edit_text("Произошла ошибка. Попробуйте ещё раз.")
        except:
            pass


@router.callback_query(F.data.startswith("dish_no_"))
async def callback_dish_no(callback: CallbackQuery):
    """
    Handle dish rejection: User rejected the recognized dish

    Flow: await_dish -> await_alt
    """
    try:
        await callback.answer()

        # Extract message_id from callback data
        message_id = int(callback.data.split("_")[-1])
        chat_id = str(callback.message.chat.id)

        logger.info(f"Dish rejected for message {message_id}")

        # Get draft from database
        draft = await get_draft(chat_id, message_id)

        if not draft:
            await callback.message.edit_text("Ошибка: данные не найдены.")
            logger.error(f"Draft not found for message {message_id}")
            return

        # Parse candidates
        candidates = safe_parse_candidates(draft.candidates)

        if not candidates or len(candidates) <= 1:
            await callback.message.edit_text(
                "К сожалению, других вариантов нет. "
                "Используйте команду /v для ручного ввода."
            )
            logger.warning(f"No alternatives available for draft {draft.id}")
            return

        # Get alternative candidates (skip first one)
        alternatives = [c.get("dish", "") for c in candidates[1:3]]  # Max 2 alternatives

        # Update draft status
        await update_draft(draft_id=draft.id, status="await_alt")

        logger.info(f"Draft {draft.id} updated: status=await_alt")

        # Show alternatives keyboard
        alt_text = (
            "Выберите один из вариантов:"
        )

        await callback.message.edit_text(
            text=alt_text,
            reply_markup=alternatives_keyboard(message_id, alternatives)
        )

    except Exception as e:
        logger.error(f"Error in dish_no callback: {e}", exc_info=True)
        try:
            await callback.message.edit_text("Произошла ошибка. Попробуйте ещё раз.")
        except:
            pass


@router.callback_query(F.data.startswith("alt_"))
async def callback_alternative(callback: CallbackQuery):
    """
    Handle alternative dish selection

    Flow: await_alt -> await_weight
    """
    try:
        await callback.answer()

        # Parse callback data: alt_{idx}_{message_id}
        parts = callback.data.split("_")
        alt_idx = int(parts[1])
        message_id = int(parts[2])
        chat_id = str(callback.message.chat.id)

        logger.info(f"Alternative {alt_idx} selected for message {message_id}")

        # Get draft from database
        draft = await get_draft(chat_id, message_id)

        if not draft:
            await callback.message.edit_text("Ошибка: данные не найдены.")
            logger.error(f"Draft not found for message {message_id}")
            return

        # Parse candidates
        candidates = safe_parse_candidates(draft.candidates)

        if not candidates or alt_idx >= len(candidates):
            await callback.message.edit_text("Ошибка: вариант не найден.")
            logger.error(f"Alternative index {alt_idx} out of range")
            return

        # Get selected alternative (remember: alt_idx starts from 1, candidates[0] is skipped)
        selected_candidate = candidates[alt_idx]
        chosen_dish = selected_candidate.get("dish", "неизвестное блюдо")
        predicted_grams = selected_candidate.get("grams", draft.grams_pred or 100)

        # Update draft
        await update_draft(
            draft_id=draft.id,
            chosen_name=chosen_dish,
            grams_pred=predicted_grams,
            status="await_weight"
        )

        logger.info(
            f"Draft {draft.id} updated: chosen_name={chosen_dish}, "
            f"grams_pred={predicted_grams}, status=await_weight"
        )

        # Show weight selection keyboard
        weight_text = (
            f"{chosen_dish}\n\n"
            f"Выберите вес:"
        )

        await callback.message.edit_text(
            text=weight_text,
            reply_markup=weight_selection_keyboard(message_id, predicted_grams)
        )

    except Exception as e:
        logger.error(f"Error in alternative callback: {e}", exc_info=True)
        try:
            await callback.message.edit_text("Произошла ошибка. Попробуйте ещё раз.")
        except:
            pass


@router.callback_query(F.data.startswith("weight_"))
async def callback_weight(callback: CallbackQuery):
    """
    Handle weight selection

    Flow: await_weight -> done
    Creates meal in database and shows confirmation
    """
    try:
        await callback.answer()

        # Parse callback data: weight_{grams}_{message_id}
        parts = callback.data.split("_")
        selected_grams = int(parts[1])
        message_id = int(parts[2])
        chat_id = str(callback.message.chat.id)

        logger.info(f"Weight {selected_grams}g selected for message {message_id}")

        # Get draft from database
        draft = await get_draft(chat_id, message_id)

        if not draft:
            await callback.message.edit_text("Ошибка: данные не найдены.")
            logger.error(f"Draft not found for message {message_id}")
            return

        if not draft.chosen_name:
            await callback.message.edit_text("Ошибка: блюдо не выбрано.")
            logger.error(f"No chosen_name in draft {draft.id}")
            return

        # Show calculating message
        await callback.message.edit_text("Рассчитываю КБЖУ...")

        # Calculate nutrition
        nutrition = await calculate_nutrition(draft.chosen_name, selected_grams)

        dish = nutrition.get("dish", draft.chosen_name)
        kcal = nutrition.get("kcal", 0)
        prot = nutrition.get("prot", 0)
        fat = nutrition.get("fat", 0)
        carb = nutrition.get("carb", 0)

        logger.info(
            f"Nutrition calculated for {dish} ({selected_grams}g): "
            f"{kcal} kcal, P:{prot} F:{fat} C:{carb}"
        )

        # Create meal in database
        eaten_at = now_msk()
        meal = await create_meal(
            chat_id=chat_id,
            dish=dish,
            grams=selected_grams,
            kcal=kcal,
            prot=prot,
            fat=fat,
            carb=carb,
            eaten_at=eaten_at
        )

        # Update draft status to done
        await update_draft(draft_id=draft.id, status="done")

        logger.info(f"Meal {meal.id} created successfully")

        # Show confirmation with cancel button
        confirmation_text = (
            f"{dish} ({selected_grams} г)\n\n"
            f"КБЖУ:\n"
            f"  Калории: {kcal} ккал\n"
            f"  Белки: {prot} г\n"
            f"  Жиры: {fat} г\n"
            f"  Углеводы: {carb} г\n\n"
            f"Время: {format_datetime_msk(eaten_at)}\n\n"
            f"Сохранено!"
        )

        await callback.message.edit_text(
            text=confirmation_text,
            reply_markup=cancel_meal_keyboard(meal.id)
        )

    except Exception as e:
        logger.error(f"Error in weight callback: {e}", exc_info=True)
        try:
            await callback.message.edit_text(
                "Произошла ошибка при сохранении. Попробуйте ещё раз."
            )
        except:
            pass


@router.callback_query(F.data.startswith("cancel_"))
async def callback_cancel_meal(callback: CallbackQuery):
    """
    Handle meal cancellation (soft delete)

    Marks meal as deleted in database
    """
    try:
        await callback.answer()

        # Extract meal_id from callback data
        meal_id = int(callback.data.split("_")[1])

        logger.info(f"Canceling meal {meal_id}")

        # Get meal to show info
        meal = await get_meal_by_id(meal_id)

        if not meal:
            await callback.message.edit_text("Ошибка: запись не найдена.")
            logger.error(f"Meal {meal_id} not found")
            return

        # Soft delete meal
        success = await soft_delete_meal(meal_id)

        if success:
            logger.info(f"Meal {meal_id} soft deleted")

            # Update message
            await callback.message.edit_text(
                f"{meal.dish} ({meal.grams} г)\n\n"
                f"Запись удалена."
            )
        else:
            await callback.message.edit_text("Ошибка при удалении записи.")
            logger.error(f"Failed to delete meal {meal_id}")

    except Exception as e:
        logger.error(f"Error in cancel callback: {e}", exc_info=True)
        try:
            await callback.message.edit_text("Произошла ошибка. Попробуйте ещё раз.")
        except:
            pass


# Catch-all for unknown callbacks
@router.callback_query()
async def callback_unknown(callback: CallbackQuery):
    """Handle unknown callback queries"""
    logger.warning(f"Unknown callback: {callback.data}")
    await callback.answer("Неизвестная команда", show_alert=False)
