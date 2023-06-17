from typing import Dict, List, Tuple, Union, Set

from aiogram import flags, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from texttable import Texttable
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, FSInputFile, InputMediaPhoto
from handlers.users.games.minesweeper.generators import generate_square_field, generate_custom
from handlers.users.games.minesweeper.keyboards.kb_newgame import make_newgame_keyboard
from handlers.users.games.minesweeper.states import ClickMode, CellMask
from loader import bot

from utils.main.minesweeper import Minesweeper


def get_fake_newgame_data(size: int, bombs: int) -> Dict:
    """
    Prepares a new game dictionary
    :param size: field size (a field is a size x size square)
    :param bombs: number of bombs to place
    :return: a dictionary with field data for a new game
    """
    result = {"current_mode": ClickMode.CLICK, "size": size, "bombs": bombs, "initial": True}
    field = generate_square_field(size)
    for x in range(size):
        for y in range(size):
            field[x][y] = {"value": field[x][y], "mask": CellMask.HIDDEN, "x": x, "y": y}
    result["cells"] = field
    return result


def get_real_game_data(size: int, bombs: int, predefined: Tuple[int, int]) -> List[List[Dict]]:
    field = generate_custom(size, bombs, predefined)
    for x in range(size):
        for y in range(size):
            field[x][y] = {"value": field[x][y], "mask": CellMask.HIDDEN, "x": x, "y": y}
    return field


def untouched_cells_count(cells: List[List[Dict]]) -> int:
    """
    Counts the number of "untouched" cells: those which status is HIDDEN
    :param cells: array of array of cells dicts
    :return: number of cells with HIDDEN status
    """
    counter = 0
    for row in cells:
        for cell in row:
            if cell["mask"] == CellMask.HIDDEN:
                counter += 1
    return counter


def all_flags_match_bombs(cells: List[List[Dict]]) -> bool:
    """
    Checks whether all flags are placed correctly
    and there are no flags over regular cells (not bombs)
    :param cells: list of list of cells dicts
    :return: True if all flags are placed correctly
    """
    for row in cells:
        for cell in row:
            if cell["mask"] == CellMask.FLAG and cell["value"] != "*":
                return False
    return True


def all_free_cells_are_open(cells: List[List[Dict]]) -> bool:
    """
    Checks whether all non-bombs cells are open
    :param cells: array of array of cells dicts
    :return: True if all non-bombs cells are in OPEN state
    """
    hidden_cells_count = 0
    for row in cells:
        for cell in row:
            if cell["mask"] != CellMask.OPEN and cell["value"] != "*":
                hidden_cells_count += 1
    return hidden_cells_count == 0


class CellsChecker:
    """
    This is a special class to check minefield cells
    """

    ROW = 0  # first item in tuple is row
    COL = 1  # second item in tuple is column

    def __init__(self, cells: List[List[Union[Dict, int]]]):
        self.cells = cells
        self.size = len(cells)
        self.checked_cells: Set[Tuple[int, int]] = set()

    def get_cells_to_open(self, cell: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        When user clicks on empty (value 0) field, we need to open all adjacent cells
        until there is a non-zero cell in every direction.
        We use depth search to find all cells to open
        This function is called recursively until every non-zero adjacent cell is found
        :param cell: a tuple containing row and column coordinates of cell to check
        :return: list of cells which must be open
        """
        result = [cell]

        # current_cell_value is always a dict except when running tests
        current_cell_value = self.cells[cell[self.ROW]][cell[self.COL]]
        if isinstance(current_cell_value, Dict):
            current_cell_value = current_cell_value["value"]

        if current_cell_value != 0:
            return result

        self.checked_cells.add(cell)

        adjacent_cells = (
            (cell[self.ROW] - 1, cell[self.COL]),  # up
            (cell[self.ROW] + 1, cell[self.COL]),  # down
            (cell[self.ROW], cell[self.COL] - 1),  # left
            (cell[self.ROW], cell[self.COL] + 1),  # right
            (cell[self.ROW] - 1, cell[self.COL] - 1),  # up left
            (cell[self.ROW] - 1, cell[self.COL] + 1),  # up right
            (cell[self.ROW] + 1, cell[self.COL] - 1),  # down left
            (cell[self.ROW] + 1, cell[self.COL] + 1),  # down right
        )

        for row_index, col_index in adjacent_cells:
            if 0 <= row_index < self.size \
                    and 0 <= col_index < self.size \
                    and (row_index, col_index) not in self.checked_cells:
                result += self.get_cells_to_open((row_index, col_index))
        return list(set(result))


def gather_open_cells(
        cells: List[List[Union[Dict, int]]],
        current: Tuple[int, int],
) -> List[Tuple[int, int]]:
    """
    If current cell stores value 0, find the whole block of numbers.
    A search goes in all directions until every direction has non-zero values
    Note: integer arrays are allowed to run tests
    :param cells: array of array of cells dicts
    :param current: (row, column) of the current cell
    :return: after all recursion calls, returns unique list of cells coordinates in block
    """

    checker = CellsChecker(cells)
    return checker.get_cells_to_open(current)


def make_text_table(cells: List[List[Dict]]) -> str:
    """
    Makes a text representation of game field using texttable library
    :param cells: array of array of cells dicts
    :return: a pretty-formatted field
    """
    table = Texttable()
    cells_size = len(cells)
    table.set_cols_width([3] * cells_size)
    table.set_cols_align(["c"] * cells_size)

    data_rows = []
    for cell_row in cells:
        data_single_row = []
        for cell in cell_row:
            cell_mask = cell["mask"]
            if cell_mask == CellMask.OPEN:
                data_single_row.append(cell["value"])
            elif cell_mask == CellMask.HIDDEN:
                if cell["value"] == "*":
                    data_single_row.append("💣")
                else:
                    data_single_row.append("⬜")
            elif cell_mask == CellMask.FLAG:
                if cell["value"] == "*":
                    data_single_row.append("🚩")
                else:
                    data_single_row.append("🚫")
            elif cell_mask == CellMask.BOMB:
                data_single_row.append("💥")
        data_rows.append(data_single_row)
    table.add_rows(data_rows, header=False)
    return f"<code>{table.draw()}</code>"


@flags.throttling_key('games')
async def show_newgame_cb(call: CallbackQuery):
    await call.message.delete_reply_markup()
    await call.message.edit_text(
        "💣 Нажмите кнопку ниже, чтобы начать новую игру (предыдущая будет закрыта)\n"
        "⚠ «Примечание: поля 6×6 и 7×7 лучше всего смотрятся на больших экранах или в настольных приложениях».",

        reply_markup=make_newgame_keyboard(call.from_user.id)
    )


@flags.throttling_key('games')
async def show_newgame_msg(message: Message, state: FSMContext):
    await state.update_data(key="somevalue")
    await message.answer(
        "💣 Нажмите кнопку ниже, чтобы начать новую игру (предыдущая будет закрыта)\n"
        "⚠ Примечание: поля 6×6 и 7×7 лучше всего смотрятся на больших экранах или в настольных приложениях.",
        reply_markup=make_newgame_keyboard(message.from_user.id)
    )


@flags.throttling_key('games')
async def stats_minesweeper(message: Message):
    await message.answer(
        f"{Minesweeper.show_stats(message)}"
    )


def list_mine(count):
    list_clans = InlineKeyboardBuilder()
    if count == 1:
        list_clans3 = InlineKeyboardButton(text='🔜 Дальше', callback_data=f'mineorder_{count + 1}')
        list_clans.add(list_clans3)
    elif count == 5:
        list_clans2 = InlineKeyboardButton(text='🔙 Назад', callback_data=f'mineorder_{count - 1}')
        list_clans.add(list_clans2)
    elif count > 1:
        list_clans2 = InlineKeyboardButton(text='🔙 Назад', callback_data=f'mineorder_{count - 1}')
        list_clans3 = InlineKeyboardButton(text='🔜 Дальше', callback_data=f'mineorder_{count + 1}')
        list_clans.add(list_clans2, list_clans3)
    return list_clans.as_markup()


@flags.throttling_key('games')
async def Mine_help_handler1(message: Message):
    photo = FSInputFile("assets/mine/minesweeper1.png")
    await bot.send_photo(chat_id=message.chat.id, photo=photo, caption='<u>Инструкция:</u> \n'
                                                                       'Как играть в эту игру, похожую на «Сапера», и какие элементы управления вы можете использовать.\n'
                                                                       'После того, как выберете режим игры, например, поле 5х5 с 3 бомбами, вы увидите поле, полные квадратами.\n'
                                                                       'Эти квадраты являются закрытыми (не обнаруживаются) ячейками . Чтобы открыть ячейку, просто нажмите на нее.',
                         reply_markup=list_mine(1))


@flags.throttling_key('games')
async def Mine_help_handler(call: CallbackQuery):
    count = int(call.data.split('_')[1])
    if count == 1:
        photo = InputMediaPhoto(media=FSInputFile("assets/mine/minesweeper1.png"), caption='Инструкция: \n'
                                                                                           'Как играть в эту игру, похожую на «Сапера», и какие элементы управления вы можете использовать.\n'
                                                                                           'После того, как выберете режим игры, например, поле 5х5 с 3 бомбами, вы увидите поле, полные квадратами.\n'
                                                                                           'Эти квадраты являются закрытыми (не обнаруживаются) ячейками . Чтобы открыть ячейку, просто нажмите на нее.', )
        await bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id, media=photo,
                                     reply_markup=list_mine(count))

    elif count == 2:
        photo = InputMediaPhoto(media=FSInputFile("assets/mine/minesweeper2.png"),
                                caption='Когда вы обнаружите больше ячеек, заметите, что некоторые из них пусты, а на некоторых из них проверены числа. \n'
                                        'Цифра означает, в радиусе 1 квадрат есть {число} бомб.\n '
                                        'Пустая ячейка означает, что поблизости нет бомб и такие ящики часто открываются.\n')
        await bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id, media=photo,
                                     reply_markup=list_mine(count))

    elif count == 3:
        photo = InputMediaPhoto(media=FSInputFile("assets/mine/minesweeper3.png"),
                                caption='Вы можете поставить флажок, чтобы закрыть все закрытые контейнеры, содержащие бомбы.\n'
                                        'Как установить флажок? Сначала переключитесь в режим Флага, затем нажмите на закрытую ячейку. \n'
                                        'Чтобы удалить флажок, нажмите на него еще раз.\n\n'
                                        '<i>Примечание: флаги используются для удобства, и для завершения игры вам не нужно ставить никаких флагов, а только захвотить все квадраты без бомб.</i>'
                                )
        await bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id, media=photo,
                                     reply_markup=list_mine(count))
    elif count == 4:
        photo = InputMediaPhoto(media=FSInputFile("assets/mine/minesweeper4.png"),
                                caption='После того, как вы закончите текущую игру, вы увидите поле с текстом и две кнопки. \n'
                                        'Первый позволяет начать новую игру с теми же настройками игры (размер полей и количество бомб), \n'
                                        'а второй за использование к выбору режима игры.')
        await bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id, media=photo,
                                     reply_markup=list_mine(count))
    elif count == 5:
        photo = InputMediaPhoto(media=FSInputFile("assets/mine/minesweeper5.png")
                                , caption='Вот описание эмодзи, использованного в тексте результата:\n'
                                          '🚩 — правильно установленный флажок\n'
                                          '💣 — незакрытая бомба (ячейка с бомбой, которая не была открыта или отмечена флажком)\n'
                                          '🚫 — неправильно установленный флажок (под этой ячейкой не было бомбы)\n'
                                          '💥 — бомба, которую вы нажали\n'
                                          '0, 1, 2, 3... — открытые коробки с соседними 0, 1, 2, 3... бомбами\n'
                                          '• — закрытая (не открытая) ячейка')
        await bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id, media=photo,
                                     reply_markup=list_mine(count))
