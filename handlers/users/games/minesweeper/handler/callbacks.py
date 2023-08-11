from contextlib import suppress
from uuid import uuid4

from aiogram import types, Router, flags

from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext

from handlers.users.games.minesweeper.game import get_fake_newgame_data, get_real_game_data, make_text_table, \
    gather_open_cells, all_free_cells_are_open, untouched_cells_count, all_flags_match_bombs
from handlers.users.games.minesweeper.keyboards.kb_minefield import make_keyboard_from_minefield
from handlers.users.games.minesweeper.keyboards.kb_newgame import NewGameCallbackFactory, ClickCallbackFactory, \
    make_replay_keyboard, SwitchModeCallbackFactory, SwitchFlagCallbackFactory, IgnoreCallbackFactory
from handlers.users.games.minesweeper.states import ClickMode, CellMask
from middlewares.check_active_game import CheckActiveGameMiddleware
from utils.main.cash import to_str
from utils.main.minesweeper import Minesweeper
from utils.main.users import User
from utils.quests.main import QuestUser

router = Router()

router.callback_query.middleware(CheckActiveGameMiddleware())


@router.callback_query(NewGameCallbackFactory.filter())
@flags.throttling_key('games')
async def callback_newgame(call: types.CallbackQuery, state: FSMContext, callback_data: NewGameCallbackFactory):
    try:

        size = callback_data.size
        bombs = callback_data.bombs
        game_id = str(uuid4())
        newgame_dict = {"game_id": game_id, "game_data": get_fake_newgame_data(size, bombs)}
        await state.set_data(newgame_dict)

        text = f"💣 Сейчас вы играете в поле <b>{size}×{size}</b>, <b>{bombs}</b> бомбы"
        kb = make_keyboard_from_minefield(newgame_dict["game_data"]["cells"], game_id, ClickMode.CLICK,
                                          call.from_user.id)

        if callback_data.as_separate:
            await call.message.delete_reply_markup()
            await call.message.edit_text(text, reply_markup=kb)
        else:
            await call.message.edit_text(text, reply_markup=kb)
        await call.answer()
    except Exception as e:
        print(e)


@router.callback_query(ClickCallbackFactory.filter(), flags={"need_check_game": True})
@flags.throttling_key('games')
async def callback_open_square(call: types.CallbackQuery, state: FSMContext,
                               callback_data: ClickCallbackFactory):
    """
    Called when player clicks a HIDDEN cell (without any flags or numbers)
    """
    try:
        user = User(user=call.from_user)
        fsm_data = await state.get_data()
        game_id = fsm_data.get("game_id")
        game_data = fsm_data.get("game_data", {})
        field_size = int(game_data.get("size"))
        bombs = int(game_data.get("bombs"))

        x = callback_data.x
        y = callback_data.y

        # If this is the first click, it's time to generate the real game field
        if game_data["initial"] is True:
            cells = get_real_game_data(game_data["size"], game_data["bombs"], (x, y))
            game_data["cells"] = cells
            game_data["initial"] = False
        else:
            cells = game_data.get("cells")

        # This cell contained a bomb
        if cells[x][y]["value"] == "*":
            cells[x][y]["mask"] = CellMask.BOMB
            with suppress(TelegramBadRequest):

                await call.message.edit_text(
                    call.message.html_text + f"\n\n{make_text_table(cells).replace('0', '0️⃣').replace('1', '1️⃣').replace('2', '2️⃣').replace('3', '3️⃣').replace('4', '4️⃣').replace('5', '5️⃣').replace('6', '6️⃣').replace('7', '7️⃣').replace('8', '8️⃣')}"
                                             f"\n\n<b>Ты проиграл</b> 😞",
                    reply_markup=make_replay_keyboard(field_size, bombs, call.from_user.id)
                )
            Minesweeper.create(game_id, call.from_user.id, fsm_data["game_data"]["size"], victory=False)
        # This cell contained a number
        else:
            # If cell is empty (0), open all adjacent squares
            if cells[x][y]["value"] == 0:
                for item in gather_open_cells(cells, (x, y)):
                    cells[item[0]][item[1]]["mask"] = CellMask.OPEN
            # ... or just the current one
            else:
                cells[x][y]["mask"] = CellMask.OPEN

            if all_free_cells_are_open(cells):

                if 5 == field_size:
                    prize = 50_000
                elif 6 == field_size:
                    prize = 100_000
                elif 7 == field_size:
                    prize = 250_000
                with suppress(TelegramBadRequest):
                    await call.message.edit_text(
                        call.message.html_text + f"\n\n{make_text_table(cells).replace('0', '0️⃣').replace('1', '1️⃣').replace('2', '2️⃣').replace('3', '3️⃣').replace('4', '4️⃣').replace('5', '5️⃣').replace('6', '6️⃣').replace('7', '7️⃣').replace('8', '8️⃣')}"
                                                 f"\n\n<b>🎉 Ты выйграл! Приз: {to_str(prize)}</b> ",
                        reply_markup=make_replay_keyboard(field_size, bombs, call.from_user.id)
                    )

                Minesweeper.create(game_id, call.from_user.id, fsm_data["game_data"]["size"], victory=True)
                user.edit('balance', user.balance + prize)
                result = QuestUser(user_id=user.id).update_progres(quest_ids=4, add_to_progresses=1)
                if result != '':
                    await call.message.answer(text=result.format(user=user.link), disable_web_page_preview=True)
                await call.answer()

                return
            # There are more flags than there should be
            elif untouched_cells_count(cells) == 0 and not all_flags_match_bombs(cells):
                await state.update_data(game_data=game_data)
                with suppress(TelegramBadRequest):
                    await call.message.edit_reply_markup(
                        reply_markup=make_keyboard_from_minefield(cells, game_id, game_data["current_mode"],
                                                                  call.from_user.id)
                    )
                await call.answer(
                    show_alert=True,
                    text="🚩 Похоже, вы установили больше флагов, чем бомб на поле. Пожалуйста, проверьте их еще раз."
                )
                return
            # If this is not the last cell to open
            else:
                await state.update_data(game_data=game_data)
                with suppress(TelegramBadRequest):
                    await call.message.edit_reply_markup(
                        reply_markup=make_keyboard_from_minefield(cells, game_id, game_data["current_mode"],
                                                                  call.from_user.id)
                    )
        await call.answer(cache_time=2)
    except Exception as e:
        print(1, e)


@router.callback_query(SwitchModeCallbackFactory.filter(), flags={"need_check_game": True})
@flags.throttling_key('games')
async def switch_click_mode(call: types.CallbackQuery, state: FSMContext, callback_data: SwitchModeCallbackFactory):
    """
    Called when player switches from CLICK (open) mode to FLAG mode
    """
    fsm_data = await state.get_data()
    game_id = fsm_data.get("game_id")
    game_data = fsm_data.get("game_data", {})
    cells = game_data.get("cells")

    if game_data["initial"] is True:
        await call.answer(show_alert=True, text="🚩 Вы можете размещать флаги только после первого клика!")
        return

    game_data["current_mode"] = callback_data.new_mode
    await state.update_data(game_data=game_data)

    with suppress(TelegramBadRequest):
        await call.message.edit_reply_markup(
            reply_markup=make_keyboard_from_minefield(cells, game_id, game_data["current_mode"], call.from_user.id)
        )
    await call.answer()


@router.callback_query(SwitchFlagCallbackFactory.filter(), flags={"need_check_game": True})
@flags.throttling_key('games')
async def add_or_remove_flag(call: types.CallbackQuery, state: FSMContext,
                             callback_data: SwitchFlagCallbackFactory):
    """
    Called when player puts a flag on HIDDEN cell or clicks a flag to remove it
    """
    fsm_data = await state.get_data()
    game_id = fsm_data.get("game_id")
    game_data = fsm_data.get("game_data", {})
    cells = game_data.get("cells")
    field_size = int(game_data.get("size"))
    bombs = int(game_data.get("bombs"))

    action = callback_data.action
    flag_x = callback_data.x
    flag_y = callback_data.y
    user = User(user=call.from_user)

    if action == "remove":
        cells[flag_x][flag_y].update(mask=CellMask.HIDDEN)
        await state.update_data(game_data=game_data)
        with suppress(TelegramBadRequest):
            await call.message.edit_reply_markup(
                reply_markup=make_keyboard_from_minefield(cells, game_id, game_data["current_mode"], call.from_user.id)
            )
    elif action == "add":
        cells[flag_x][flag_y].update(mask=CellMask.FLAG)
        # See callback_open_square() for explanation
        if untouched_cells_count(cells) == 0:
            if all_flags_match_bombs(cells):
                if 5 == field_size:
                    prize = 50_000
                elif 6 == field_size:
                    prize = 100_000
                elif 7 == field_size:
                    prize = 250_000
                with suppress(TelegramBadRequest):
                    await call.message.edit_text(
                        call.message.html_text + f"\n\n{make_text_table(cells).replace('0', '0️⃣').replace('1', '1️⃣').replace('2', '2️⃣').replace('3', '3️⃣').replace('4', '4️⃣').replace('5', '5️⃣').replace('6', '6️⃣').replace('7', '7️⃣').replace('8', '8️⃣')}"
                                                 f"\n\n<b>🎉 Ты выйграл! Приз: {to_str(prize)}</b> ",
                        reply_markup=make_replay_keyboard(field_size, bombs, call.from_user.id)
                    )

                user.edit('balance', user.balance + prize)
                Minesweeper.create(game_id, call.from_user.id, fsm_data["game_data"]["size"], victory=True)
                result = QuestUser(user_id=user.id).update_progres(quest_ids=4, add_to_progresses=1)
                if result != '':
                    await call.message.answer(text=result.format(user=user.link), disable_web_page_preview=True)
            else:
                await state.update_data(game_data=game_data)
                with suppress(TelegramBadRequest):
                    await call.message.edit_reply_markup(
                        reply_markup=make_keyboard_from_minefield(cells, game_id, game_data["current_mode"],
                                                                  call.from_user.id)
                    )
                await call.answer(
                    show_alert=True,
                    text="🚩 Похоже, вы установили больше флагов, чем бомб на поле. "
                         "Пожалуйста, проверьте их еще раз."
                )
                return
        else:
            await state.update_data(game_data=game_data)
            with suppress(TelegramBadRequest):
                await call.message.edit_reply_markup(
                    reply_markup=make_keyboard_from_minefield(cells, game_id, game_data["current_mode"],
                                                              call.from_user.id)
                )
    await call.answer(cache_time=1)


@router.callback_query(IgnoreCallbackFactory.filter())
@flags.throttling_key('games')
async def callback_ignore(call: types.CallbackQuery):
    """
    Called when player clicks on an open number.
    In this case, we simply ignore this callback.
    """
    await call.answer(cache_time=3)
