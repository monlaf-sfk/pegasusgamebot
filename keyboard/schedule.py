from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class ScheduleCallback(CallbackData, prefix="run"):
    user_id: int
    action: str


def schedue_kb(user_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text=f"За спавнить босса",
                             callback_data=ScheduleCallback(action="boss_spavn", user_id=user_id).pack())
    )
    keyboard.add(
        InlineKeyboardButton(text=f"За постить промо",
                             callback_data=ScheduleCallback(action="autopromo_run", user_id=user_id).pack())
    )
    keyboard.add(
        InlineKeyboardButton(text=f"Сменить курс биткоина евро юаня",
                             callback_data=ScheduleCallback(action="btc_change_run", user_id=user_id).pack())
    )

    keyboard.adjust(1)
    return keyboard.as_markup()
