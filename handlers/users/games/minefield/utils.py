import random

from typing import List, Dict

from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import StatesGroup, State

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

ROWS = 4
COLS = 3


class CellMask:
    HIDDEN = 0
    OPEN = 1
    EMPTY = 2
    BOMB = 3
    CHECKED = 4


class ClickMode:
    START = 0
    TAKE = 2
    FINISH = 3


class ClickCallbackFactory(CallbackData, prefix="press"):
    game_id: str
    user_id: int
    column: int
    row: int


class NewGameCallbackFactory(CallbackData, prefix="press"):
    summ: int
    user_id: int


class IgnoreCallbackFactory(CallbackData, prefix="ignore"):
    user_id: int
    column: int
    row: int


class StopCallbackFactory(CallbackData, prefix="stop"):
    game_id: str
    user_id: int
    summ: int


class MineField(StatesGroup):
    waiting_for_action = State()


def mine_create():
    minefield = [[False] * COLS for _ in range(ROWS)]  # Создаем список из False
    for sublist in minefield:
        random_index = random.randint(0, COLS - 1)  # Генерируем случайный индекс
        sublist[random_index] = True
    return minefield


def get_real_game_data(minefield) -> List[List[Dict]]:
    real_game_data = []
    for indx_r, row in enumerate(minefield):
        row_data = []  # Store row data for each column
        for indx_c, cell_value in enumerate(row):
            cell_data = {
                "value": cell_value,
                "mask": CellMask.HIDDEN,
                "column": indx_c,
                "row": indx_r
            }
            row_data.append(cell_data)

        real_game_data.append(row_data)

    return real_game_data


def generated_keyboard(game_id, minefield, user_id, click_mode, summ5):
    keyboard = InlineKeyboardBuilder()
    for cells_row in minefield:
        kb_row = []
        for cell in cells_row:

            mask_value = cell["mask"]
            column = cell["column"]
            row = cell["row"]
            # Check statuses
            if mask_value == CellMask.HIDDEN:
                if minefield[row - 1][column]["mask"] == CellMask.HIDDEN and row == 0:
                    btn = InlineKeyboardButton(text="«❓»")
                    btn.callback_data = ClickCallbackFactory(game_id=game_id, column=column, row=row,
                                                             user_id=user_id).pack()
                elif minefield[row - 1][column]["mask"] == CellMask.HIDDEN:
                    btn = InlineKeyboardButton(text="❓")
                    btn.callback_data = ClickCallbackFactory(game_id=game_id, column=column, row=row,
                                                             user_id=user_id).pack()
                else:
                    btn = InlineKeyboardButton(text="«❓»")
                    btn.callback_data = ClickCallbackFactory(game_id=game_id, column=column, row=row,
                                                             user_id=user_id).pack()
            elif mask_value == CellMask.CHECKED:
                btn = InlineKeyboardButton(
                    text="✅",
                    callback_data=IgnoreCallbackFactory(column=column, row=row, user_id=user_id).pack()
                )
            elif mask_value == CellMask.OPEN:
                val = cell["value"]
                if val == 0:
                    val = "⠀"  # Empty symbol
                if val == True:
                    val = "💣"
                btn = InlineKeyboardButton(text=str(val),
                                           callback_data=IgnoreCallbackFactory(column=column, row=row,
                                                                               user_id=user_id).pack())
            kb_row.append(btn)
        keyboard.row(*kb_row)
    if click_mode == ClickMode.FINISH:
        switch_mode_btn = InlineKeyboardButton(
            text="💣 Начать заново",
            callback_data=NewGameCallbackFactory(user_id=user_id, summ=summ5).pack()
        )
    elif click_mode == ClickMode.TAKE:
        switch_mode_btn = InlineKeyboardButton(
            text="💸 Забрать деньги",
            callback_data=StopCallbackFactory(game_id=game_id, user_id=user_id, summ=summ5).pack())
    if click_mode != ClickMode.START:
        keyboard.row(switch_mode_btn)
    return keyboard.as_markup()


def generate_minefield_text(minefield):
    minefield_text = ""
    for cells_row in minefield:
        row_text = ""
        for cell in cells_row:
            mask_value = cell["mask"]
            column = cell["column"]
            row = cell["row"]
            if mask_value == CellMask.HIDDEN:
                if minefield[row - 1][column]["mask"] == CellMask.HIDDEN and row == 0:
                    row_text += "«❓»"
                elif minefield[row - 1][column]["mask"] == CellMask.HIDDEN:
                    row_text += "[❓]"
                else:
                    row_text += "«❓»"
            elif mask_value == CellMask.CHECKED:
                row_text += "[✅]"
            elif mask_value == CellMask.OPEN:
                val = cell["value"]
                if val == 0:
                    row_text += "[⠀   ]"
                elif val == True:
                    row_text += "[💣]"
                else:
                    row_text += f"[{val}]"
        minefield_text += row_text + "\n"
    return minefield_text
