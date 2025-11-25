from typing import List
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def dish_confirmation_keyboard(message_id: int) -> InlineKeyboardMarkup:
    """
    Keyboard for dish confirmation (Yes/No)

    Args:
        message_id: Message ID for callback data
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Да",
                callback_data=f"dish_yes_{message_id}"
            ),
            InlineKeyboardButton(
                text="❌ Нет",
                callback_data=f"dish_no_{message_id}"
            )
        ]
    ])


def alternatives_keyboard(
    message_id: int,
    alternatives: List[str]
) -> InlineKeyboardMarkup:
    """
    Keyboard for dish alternatives selection

    Args:
        message_id: Message ID for callback data
        alternatives: List of alternative dish names (2-3 items)
    """
    buttons = []

    for idx, dish in enumerate(alternatives, start=1):
        buttons.append([
            InlineKeyboardButton(
                text=dish,
                callback_data=f"alt_{idx}_{message_id}"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def weight_selection_keyboard(
    message_id: int,
    predicted_grams: int,
    step: int = None
) -> InlineKeyboardMarkup:
    """
    Keyboard for weight selection

    Args:
        message_id: Message ID for callback data
        predicted_grams: Predicted weight in grams
        step: Step for weight buttons (auto-calculated if None)
    """
    # Auto-calculate step based on predicted weight
    if step is None:
        if predicted_grams < 120:
            step = 20
        else:
            step = 50

    # Generate 3 buttons: -step, predicted, +step
    buttons_values = [
        predicted_grams - step,
        predicted_grams,
        predicted_grams + step
    ]

    # Filter out negative values
    buttons_values = [g for g in buttons_values if g > 0]

    buttons = [
        InlineKeyboardButton(
            text=f"{g} г",
            callback_data=f"weight_{g}_{message_id}"
        )
        for g in buttons_values
    ]

    return InlineKeyboardMarkup(inline_keyboard=[buttons])


def cancel_meal_keyboard(meal_id: int) -> InlineKeyboardMarkup:
    """
    Keyboard for canceling meal save

    Args:
        meal_id: Meal ID for callback data
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🚫 не сохранять",
                callback_data=f"cancel_{meal_id}"
            )
        ]
    ])


def custom_weight_keyboard(message_id: int) -> InlineKeyboardMarkup:
    """
    Keyboard with custom weight input option

    Args:
        message_id: Message ID for callback data
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✏️ Ввести вручную",
                callback_data=f"custom_weight_{message_id}"
            )
        ]
    ])
