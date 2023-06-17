from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class NewGameCallbackFactory(CallbackData, prefix="newgame"):
    user_id: int
    size: int
    bombs: int
    as_separate: bool


class ClickCallbackFactory(CallbackData, prefix="press"):
    user_id: int
    game_id: str
    x: int
    y: int


class SwitchFlagCallbackFactory(CallbackData, prefix="flag"):
    user_id: int
    game_id: str
    action: str
    x: int
    y: int


class SwitchModeCallbackFactory(CallbackData, prefix="switchmode"):
    user_id: int
    game_id: str
    new_mode: int


class IgnoreCallbackFactory(CallbackData, prefix="ignore"):
    user_id: int
    x: int
    y: int


def make_newgame_keyboard(user_id: int) -> InlineKeyboardMarkup:
    available_options = [
        (5, 3), (6, 5), (7, 7)  # (size, bombs)
    ]
    keyboard = InlineKeyboardBuilder()
    for size, bombs in available_options:
        keyboard.row(InlineKeyboardButton(
            text=f"⛳️ Размер поля {size}×{size},кол-во бомб (х{bombs} 💣)",
            callback_data=NewGameCallbackFactory(size=size, bombs=bombs, as_separate=False, user_id=user_id).pack()
        ))

    return keyboard.as_markup()


def make_replay_keyboard(size: int, bombs: int, user_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(
        text=f"⛳️ Новая игра ({size}×{size} поле, бомб х{bombs} 💣)",
        callback_data=NewGameCallbackFactory(size=size, bombs=bombs, as_separate=True, user_id=user_id).pack()))
    keyboard.row(InlineKeyboardButton(text="⛳️ Новая игра (другое)", callback_data="choose_newgame"))
    return keyboard.as_markup()
