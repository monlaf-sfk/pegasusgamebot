from typing import List

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from handlers.users.games.minesweeper.keyboards.kb_newgame import ClickCallbackFactory, SwitchFlagCallbackFactory, \
    SwitchModeCallbackFactory, IgnoreCallbackFactory
from handlers.users.games.minesweeper.states import CellMask, ClickMode


def make_keyboard_from_minefield(cells: List[List], game_id: str, click_mode: int,
                                 user_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for cells_row in cells:
        kb_row = []
        for cell in cells_row:
            mask_value = cell["mask"]
            x = cell["x"]
            y = cell["y"]
            # Check statuses
            if mask_value == CellMask.HIDDEN:
                btn = InlineKeyboardButton(text="⬜")
                if click_mode == ClickMode.CLICK:
                    btn.callback_data = ClickCallbackFactory(game_id=game_id, x=x, y=y, user_id=user_id).pack()
                else:
                    btn.callback_data = SwitchFlagCallbackFactory(game_id=game_id, action="add", x=x, y=y,
                                                                  user_id=user_id).pack()
            elif mask_value == CellMask.FLAG:
                btn = InlineKeyboardButton(
                    text="🚩",
                    callback_data=SwitchFlagCallbackFactory(game_id=game_id, action="remove", x=x, y=y,
                                                            user_id=user_id).pack()
                )
            else:  # mask_value == CellMask.OPEN
                val = cell["value"]
                if val == 0:
                    val = "⠀"  # Empty symbol
                btn = InlineKeyboardButton(text=str(val),
                                           callback_data=IgnoreCallbackFactory(x=x, y=y, user_id=user_id).pack())
            kb_row.append(btn)
        keyboard.row(*kb_row)

    # Add switch flag mode button
    if click_mode == ClickMode.FLAG:
        switch_mode_btn = InlineKeyboardButton(
            text="🔄 Текущий режим: Флаг",
            callback_data=SwitchModeCallbackFactory(game_id=game_id, new_mode=ClickMode.CLICK, user_id=user_id).pack()
        )
    else:
        switch_mode_btn = InlineKeyboardButton(
            text="🔄 Текущий режим: Клик",
            callback_data=SwitchModeCallbackFactory(game_id=game_id, new_mode=ClickMode.FLAG, user_id=user_id).pack()
        )
    keyboard.row(switch_mode_btn)

    return keyboard.as_markup()
