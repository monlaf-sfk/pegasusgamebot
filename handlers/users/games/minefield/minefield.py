import random
from contextlib import suppress

from uuid import uuid4

from aiogram import types, Router, Bot, F

from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command

from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey, BaseStorage

from aiogram.types import Message, CallbackQuery

from config import bot_name
from filters.triggers import Trigger
from handlers.users.games.minefield.utils import get_real_game_data, mine_create, generated_keyboard, \
    NewGameCallbackFactory, CellMask, ClickMode, StopCallbackFactory, ClickCallbackFactory, IgnoreCallbackFactory, \
    MineField
from keyboard.generate import show_balance_kb
from states.sqlite_state import get_user_state_data, update_data_and_state, set_user_data, delete_user_state
from utils.main.cash import to_str, get_cash

from utils.main.users import User

router = Router()
values = {
    0: 1.5,
    1: 2,
    2: 2.4,
    3: 3,
}
router.message.filter(F.chat.type.in_({"private"}))


async def check_state(message: Message, state: FSMContext, fsm_storage: BaseStorage, bot: Bot):
    user = User(id=message.from_user.id)
    if isinstance(message, CallbackQuery):
        message = message.message
    state_db = await get_user_state_data(int(user.id), 'MineField')
    if not state_db:
        fsm_data = await fsm_storage.get_data(
            key=StorageKey(user_id=user.id, chat_id=user.id, bot_id=bot.id))

    else:
        fsm_data = state_db["data"]

    game_id = fsm_data.get("game_id")
    step = None
    game_data = fsm_data.get("game_data", {})
    summ5 = int(fsm_data.get("summ"))

    for current_row in game_data:
        for cell in current_row:
            column = cell["column"]
            row_index = cell["row"]
            if game_data[row_index][column]["mask"] != CellMask.HIDDEN:
                step = row_index
                break  # Exit the loop if any step has been taken

    if step is None:
        return await message.reply(f'{user.link}, чтобы забрать приз, сделайте как минимум 1 ход',
                                   reply_markup=generated_keyboard(game_id, game_data, user.id,
                                                                   ClickMode.TAKE, summ5),
                                   disable_web_page_preview=True)

    prize = int(summ5 * values[step])
    user.edit('balance', user.balance + prize)
    text = f"{user.link}, Вы остановились на {step + 1} ходу 😯\n" \
           f"💸 Приз: {to_str(prize)} (x{values[step]})\n" \
           f"💰 Баланс: {to_str(user.balance)}\n"

    for row in game_data:
        for cell in row:
            column = cell["column"]
            row = cell["row"]
            if game_data[row][column]["mask"] == CellMask.HIDDEN:
                game_data[row][column]["mask"] = CellMask.OPEN

    await message.reply(text, reply_markup=generated_keyboard(game_id, game_data, user.id,
                                                              ClickMode.FINISH, summ5),
                        disable_web_page_preview=True)
    await state.set_state(None)
    await delete_user_state(int(user.id), 'waiting_for_action', 'MineField')


@router.message(Trigger(['минное поле', 'поле']))
async def start_minefield(message: Message, state: FSMContext, bot: Bot, fsm_storage: BaseStorage):
    state_db = await get_user_state_data(message.from_user.id, 'MineField')

    if not state_db:
        state_get = await fsm_storage.get_state(
            key=StorageKey(user_id=message.from_user.id, chat_id=message.from_user.id, bot_id=bot.id))
        if state_get in ['MineField:waiting_for_action']:
            return await check_state(message, state, fsm_storage, bot)
    else:
        state_map = {
            'waiting_for_action': MineField.waiting_for_action,
        }

        if state_db["state"] in state_map:
            await fsm_storage.set_data(data=state_db["data"], key=StorageKey(
                user_id=message.from_user.id,
                chat_id=message.from_user.id,
                bot_id=bot.id))
            new_state = state_map[state_db["state"]]
            await fsm_storage.set_state(state=new_state, key=StorageKey(
                user_id=message.from_user.id,
                chat_id=message.from_user.id,
                bot_id=bot.id))
            return await check_state(message, state, fsm_storage, bot)
    arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[
        0].lower() else message.text.split()[2:]
    if len(arg) > 0 and arg[0].lower() == 'поле':
        arg = message.text.split()[2:] if not bot_name.lower() in message.text.split()[
            0].lower() else message.text.split()[3:]

    user = User(user=message.from_user)
    try:
        summ5 = get_cash(arg[0] if arg[0].lower() not in ['всё', 'все'] else str(user.balance))
    except:
        summ5 = 0
    smile = ['💥', '💣', '⛳']
    rsmile = random.choice(smile)

    if len(arg) == 0:
        return await message.answer(
            f"{rsmile} {user.link}, введите «Поле [сумма ставки]»\n"
            "❓ Минимальная ставка в «Минное поле» — 5$"
            , disable_web_page_preview=True)

    if summ5 < 5:
        return await message.reply('❌ Ставка должна быть больше 5$', reply_markup=show_balance_kb.as_markup())

    if user.balance < summ5:
        return await message.reply('❌ Ошибка. Недостаточно денег на руках для ставки! 💸',
                                   reply_markup=show_balance_kb.as_markup())
    user.edit('balance', user.balance - summ5)
    text = f"{user.link}, Вы начали играть в «Минное поле» 👍🏼\n" \
           "✅ Для игры вводите номер клетки от 1 до 3\n" \
           "💸 Забрать валюту: «Поле»"

    field = get_real_game_data(mine_create())
    game_id = str(uuid4())
    await fsm_storage.set_state(state=MineField.waiting_for_action, key=StorageKey(
        user_id=message.from_user.id,
        chat_id=message.from_user.id,
        bot_id=bot.id))
    data = {"game_id": game_id, 'game_data': field, 'summ': str(summ5)}
    await fsm_storage.update_data(data=data,
                                  key=StorageKey(
                                      user_id=message.from_user.id,
                                      chat_id=message.from_user.id,
                                      bot_id=bot.id))

    await message.answer(text,
                         reply_markup=generated_keyboard(game_id, field, message.from_user.id, ClickMode.START, summ5),
                         disable_web_page_preview=True)
    if state_db:
        await update_data_and_state(message.from_user.id, data, 'waiting_for_action', 'MineField')
    else:
        await set_user_data(message.from_user.id, 'MineField', 'waiting_for_action', data)


@router.callback_query(NewGameCallbackFactory.filter())
async def start_call_minefiled(call: types.CallbackQuery, state: FSMContext, bot: Bot, fsm_storage: BaseStorage,
                               callback_data: NewGameCallbackFactory):
    state_db = await get_user_state_data(call.from_user.id, 'MineField')

    if not state_db:
        state_get = await fsm_storage.get_state(
            key=StorageKey(user_id=call.from_user.id, chat_id=call.from_user.id, bot_id=bot.id))

        if state_get in ['MineField:waiting_for_action']:
            return await check_state(call, state, fsm_storage, bot)
    else:
        await fsm_storage.set_data(data=state_db["data"], key=StorageKey(
            user_id=call.from_user.id,
            chat_id=call.from_user.id,
            bot_id=bot.id))
        state_map = {
            'waiting_for_action': MineField.waiting_for_action,

        }
        if state_db["state"] in state_map:
            new_state = state_map[state_db["state"]]
            await fsm_storage.set_state(state=new_state, key=StorageKey(
                user_id=call.from_user.id,
                chat_id=call.from_user.id,
                bot_id=bot.id))
            return await check_state(call, state, fsm_storage, bot)
    user = User(id=call.from_user.id)

    text = f"{user.link}, Вы начали играть в «Минное поле» 👍🏼\n" \
           "✅ Для игры вводите номер клетки от 1 до 3\n" \
           "💸 Забрать валюту: «Поле»"
    if callback_data.summ < 5:
        with suppress(TelegramBadRequest):
            await call.message.edit_text('❌ Ставка должна быть больше 5$', reply_markup=show_balance_kb.as_markup())
        return

    if user.balance < callback_data.summ:
        with suppress(TelegramBadRequest):
            await call.message.edit_text('❌ Ошибка. Недостаточно денег на руках для ставки! 💸',
                                         reply_markup=show_balance_kb.as_markup())
        return
    user.edit('balance', user.balance - callback_data.summ)
    field = get_real_game_data(mine_create())
    game_id = str(uuid4())
    await fsm_storage.set_state(state=MineField.waiting_for_action, key=StorageKey(
        user_id=call.from_user.id,
        chat_id=call.message.chat.id,
        bot_id=bot.id))
    data = {"game_id": game_id, 'game_data': field, 'summ': str(callback_data.summ)}
    await fsm_storage.update_data(data=data,
                                  key=StorageKey(
                                      user_id=call.from_user.id,
                                      chat_id=call.message.chat.id,
                                      bot_id=bot.id))
    with suppress(TelegramBadRequest):
        await call.message.edit_text(text,
                                     reply_markup=generated_keyboard(game_id, field, call.from_user.id, ClickMode.START,
                                                                     callback_data.summ),
                                     disable_web_page_preview=True)
    if state_db:
        await update_data_and_state(call.from_user.id, data, 'waiting_for_action', 'MineField')
    else:
        await set_user_data(call.from_user.id, 'MineField', 'waiting_for_action', data)


@router.message(Trigger(['минное поле', 'поле']), MineField.waiting_for_action)
async def stop_minefield(message: Message, state: FSMContext):
    state_db = await get_user_state_data(message.from_user.id, 'MineField')
    if not state_db:
        fsm_data = await state.get_data()
    else:
        fsm_data = state_db["data"]
    user = User(id=message.from_user.id)
    game_id = fsm_data.get("game_id")
    step = None
    game_data = fsm_data.get("game_data", {})
    summ5 = int(fsm_data.get("summ"))

    for current_row in game_data:
        for cell in current_row:
            column = cell["column"]
            row_index = cell["row"]
            if game_data[row_index][column]["mask"] != CellMask.HIDDEN:
                step = row_index
                break  # Exit the loop if any step has been taken

    if step is None:
        return await message.reply(f'{user.link}, чтобы забрать приз, сделайте как минимум 1 ход',
                                   reply_markup=generated_keyboard(game_id, game_data, message.from_user.id,
                                                                   ClickMode.TAKE, summ5),
                                   disable_web_page_preview=True)

    prize = int(summ5 * values[step])
    user.edit('balance', user.balance + prize)
    text = f"{user.link}, Вы остановились на {step + 1} ходу 😯\n" \
           f"💸 Приз: {to_str(prize)} (x{values[step]})\n" \
           f"💰 Баланс: {to_str(user.balance)}\n"

    for row in game_data:
        for cell in row:
            column = cell["column"]
            row = cell["row"]
            if game_data[row][column]["mask"] == CellMask.HIDDEN:
                game_data[row][column]["mask"] = CellMask.OPEN

    await message.reply(text, reply_markup=generated_keyboard(game_id, game_data, message.from_user.id,
                                                              ClickMode.FINISH, summ5),
                        disable_web_page_preview=True)

    await state.set_state(None)
    await delete_user_state(message.from_user.id, 'waiting_for_action', 'MineField')


@router.callback_query(StopCallbackFactory.filter(), MineField.waiting_for_action)
async def stop_call_minefield(call: types.CallbackQuery, state: FSMContext, callback_data: StopCallbackFactory):
    fsm_data = await state.get_data()
    game_id = fsm_data.get("game_id")
    if callback_data.game_id != game_id:
        return
    user = User(id=call.from_user.id)
    step = None
    game_data = fsm_data.get("game_data", {})
    summ5 = int(fsm_data.get("summ"))

    for current_row in game_data:
        for cell in current_row:
            column = cell["column"]
            row_index = cell["row"]
            if game_data[row_index][column]["mask"] != CellMask.HIDDEN:
                step = row_index
                break  # Exit the loop if any step has been taken

    if step is None:
        with suppress(TelegramBadRequest):
            return await call.message.edit_text('чтобы забрать приз, сделайте как минимум 1 ход',
                                                reply_markup=generated_keyboard(game_id, game_data, call.from_user.id,
                                                                                ClickMode.TAKE, summ5))

    prize = int(summ5 * values[step])
    user.edit('balance', user.balance + prize)
    text = f"{user.link}, Вы остановились на {step + 1} ходу 😯\n" \
           f"💸 Приз: {to_str(prize)} (x{values[step]})\n" \
           f"💰 Баланс: {to_str(user.balance)}\n"

    for row in game_data:
        for cell in row:
            column = cell["column"]
            row = cell["row"]
            if game_data[row][column]["mask"] == CellMask.HIDDEN:
                game_data[row][column]["mask"] = CellMask.OPEN
    with suppress(TelegramBadRequest):
        await call.message.edit_text(text, reply_markup=generated_keyboard(game_id, game_data, call.from_user.id,
                                                                           ClickMode.FINISH, summ5),
                                     disable_web_page_preview=True)

    await state.set_state(None)
    await delete_user_state(call.from_user.id, 'waiting_for_action', 'MineField')


@router.callback_query(ClickCallbackFactory.filter(), MineField.waiting_for_action)
async def callback_open_square(call: types.CallbackQuery, state: FSMContext,
                               callback_data: ClickCallbackFactory, bot: Bot):
    if callback_data.user_id != call.from_user.id:
        return

    fsm_data = await state.get_data()
    game_id = fsm_data.get("game_id")
    if callback_data.game_id != game_id:
        return
    user = User(id=call.from_user.id)
    game_data = fsm_data.get("game_data", {})
    summ5 = int(fsm_data.get("summ"))
    column = callback_data.column
    row = callback_data.row

    if row != 0:
        if game_data[row - 1][column]["mask"] == CellMask.HIDDEN:
            return
    if game_data[row][column]["value"] == True:
        for row_list in game_data:
            for cell in row_list:
                column2 = cell["column"]
                row2 = cell["row"]
                if game_data[row2][column2]["mask"] == CellMask.HIDDEN:
                    game_data[row2][column2]["mask"] = CellMask.OPEN

        with suppress(TelegramBadRequest):

            await call.message.edit_text(
                f"{user.link}, Вы попали на мину, ставка обнуляется 😔",
                reply_markup=generated_keyboard(game_id, game_data, call.from_user.id, ClickMode.FINISH, summ5)
                , disable_web_page_preview=True)
        await delete_user_state(call.from_user.id, 'waiting_for_action',
                                'MineField')
        await state.set_state(None)
    # This cell contained a number
    else:
        # If cell is empty (0), open all adjacent squares
        for ind, item in enumerate(game_data[row]):
            game_data[row][ind]["mask"] = CellMask.OPEN
        game_data[row][column]["mask"] = CellMask.CHECKED

        all_cells_open = True
        for row_list in game_data:
            for cell in row_list:
                column2 = cell["column"]
                row2 = cell["row"]

                if game_data[row2][column2]["mask"] == CellMask.HIDDEN:
                    all_cells_open = False
                    break  # Если хотя бы одна ячейка не открыта, выход из цикла

        if all_cells_open:
            prize = int(summ5 * values[row])
            user.edit('balance', user.balance + prize)
            with suppress(TelegramBadRequest):
                await call.message.edit_text(f"{user.link}, Вы прошли всё поле! ☺️\n"
                                             f"💸 Приз: {to_str(prize)}\n"
                                             f"💰 Баланс: {to_str(user.balance)}\n"
                                             ,
                                             reply_markup=generated_keyboard(game_id, game_data, call.from_user.id,
                                                                             ClickMode.FINISH, summ5)
                                             , disable_web_page_preview=True)
            await delete_user_state(call.from_user.id, 'waiting_for_action',
                                    'MineField')
            await state.set_state(None)
            return
        await state.update_data(game_data=game_data)
        with suppress(TelegramBadRequest):
            await call.message.edit_text(f"{user.link}, на этой клетке нет мины 👍🏻\n"
                                         f"💸 Ставка: {to_str(int(summ5 * values[row]))} (x{values[row]})",
                                         reply_markup=generated_keyboard(game_id, game_data, call.from_user.id,
                                                                         ClickMode.TAKE, summ5)
                                         , disable_web_page_preview=True)

        fsm_data = await state.get_data()
        await update_data_and_state(call.from_user.id, fsm_data, 'waiting_for_action', 'MineField')


@router.callback_query(IgnoreCallbackFactory.filter(), MineField.waiting_for_action)
async def callback_ignore(call: types.CallbackQuery):
    """
    Called when player clicks on an open number.
    In this case, we simply ignore this callback.
    """
    await call.answer(cache_time=3)
