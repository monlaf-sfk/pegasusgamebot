import time

from aiogram import Router, flags
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from filters.triggers import Trigger
from keyboard.games import tictac

from utils.main.db import sql, timetostr
from utils.main.users import User

router = Router()


class TicTacToe:
    def __init__(self, player1: int, player2: int, time, id_message):
        self.game_over = False
        self.player1 = int(player1)
        self.player2 = int(player2)
        self.board = [[' ' for _ in range(5)] for _ in range(5)]
        self.time = time
        self.id_message = id_message
        for n, row in enumerate(self.board, 0):
            for i, col in enumerate(row, 0):
                if n == 0 or i == 0 or i == 4 or n == 4:
                    self.board[n][i] = '⬜'
                else:
                    pass
        self.turn = int(player1)

    def check_win(self):
        # Check rows
        for row in self.board:
            if row == ['⬜', '❌', '❌', '❌', '⬜']:
                return True
            elif row == ['⬜', '⭕', '⭕', '⭕', '⬜']:
                return True
        # Check columns
        for col in range(5):
            if self.board[1][col] == '❌' and self.board[2][col] == '❌' and self.board[3][col] == '❌':
                return True
            elif self.board[1][col] == '⭕' and self.board[2][col] == '⭕' and self.board[3][col] == '⭕':
                return True
        # Check diagonals
        if self.board[1][1] == '❌' and self.board[2][2] == '❌' and self.board[3][3] == '❌':
            return True
        elif self.board[1][1] == '⭕' and self.board[2][2] == '⭕' and self.board[3][3] == '⭕':
            return True
        if self.board[1][3] == '❌' and self.board[2][2] == '❌' and self.board[3][1] == '❌':
            return True
        elif self.board[1][3] == '⭕' and self.board[2][2] == '⭕' and self.board[3][1] == '⭕':
            return True
        return False

    def check_tie(self):
        return all(all(val != ' ' for val in row) for row in self.board)

    def make_move(self, row, col, id):
        if id != self.turn:
            return "Не твой ход"
        if self.game_over:
            return "Игра закончена"
        if self.board[row][col] != ' ':
            return "Этот слот занят выберите другой."
        self.board[row][col] = '❌' if self.turn == self.player1 else '⭕'
        if self.check_win():
            self.game_over = True
            return self.turn
        if self.check_tie():
            self.game_over = True
            return "Игра завершилось ничьей!"

        self.turn = self.player1 if self.turn == self.player2 else self.player2
        return None


games = {}


@flags.throttling_key('default')
async def process_callback_game(callback_query: CallbackQuery):
    chat_id = callback_query.message.chat.id
    call = callback_query.data.split('tictac_')[1]
    row, col = map(int, call.split())
    game = games.get(chat_id)
    if not game:
        return await callback_query.answer("❕ Нет игр на данный момент", show_alert=False)
    if callback_query.from_user.id not in (int(game.player1), int(game.player2)):
        return await callback_query.answer("❕ Это не твоя игра.", show_alert=False)
    if callback_query.message.message_id != game.id_message:
        return await callback_query.answer("❕ Используй актуальную клавиатуру.", show_alert=False)
    result = game.make_move(row, col, callback_query.from_user.id)
    if result:
        if game.game_over == False:
            await callback_query.answer(text=result)
        else:
            keyboard = InlineKeyboardBuilder()
            for row in range(5):
                row_keyboard = []
                for col in range(5):
                    if row == 0 or col == 0 or col == 4 or row == 4:
                        button = InlineKeyboardButton(text='⬜', callback_data=f"tictac_{row} {col}")
                    else:
                        button = InlineKeyboardButton(text=game.board[row][col], callback_data=f"tictac_{row} {col}")
                    row_keyboard.append(button)
                keyboard.row(*row_keyboard)
            player1 = User(id=game.player1)
            player2 = User(id=game.player2)
            if str(result).isdigit():
                turn = User(id=result)
                await callback_query.message.edit_text(text=f'1️⃣.Игрок: {player1.link}[❌]\n'
                                                            f'2️⃣.Игрок: {player2.link}[⭕]\n'
                                                            f'➖➖➖➖➖➖➖➖➖➖➖➖\n' \
                                                            f'{turn.link} Одержал победу!',
                                                       reply_markup=keyboard.as_markup(), parse_mode='html',
                                                       disable_web_page_preview=True)
            else:
                await callback_query.message.edit_text(
                    text=f'1️⃣.Игрок: {player1.link}[❌]\n'
                         f'2️⃣.Игрок: {player2.link}[⭕]\n'
                         f'➖➖➖➖➖➖➖➖➖➖➖➖\n' \
                         f'{result}', reply_markup=keyboard.as_markup(), disable_web_page_preview=True)
            games.pop(chat_id)
    else:
        keyboard = InlineKeyboardBuilder()
        for row in range(5):
            row_keyboard = []
            for col in range(5):
                if row == 0 or col == 0 or col == 4 or row == 4:
                    button = InlineKeyboardButton(text='⬜', callback_data=f"tictac_{row} {col}")
                else:
                    button = InlineKeyboardButton(text=game.board[row][col], callback_data=f"tictac_{row} {col}")
                row_keyboard.append(button)
            keyboard.row(*row_keyboard)
        player1 = User(id=game.player1)
        player2 = User(id=game.player2)
        turn = User(id=game.turn)
        await callback_query.message.edit_text(text=f'1️⃣.Игрок: {player1.link}[❌]\n'
                                                    f'2️⃣.Игрок: {player2.link}[⭕]\n'
                                                    f'➖➖➖➖➖➖➖➖➖➖➖➖\n'
                                                    f"🧩 Ход: {turn.link} [{'❌' if game.turn == game.player1 else '⭕'}]",
                                               reply_markup=keyboard.as_markup(), parse_mode='html',
                                               disable_web_page_preview=True)


@router.message(Trigger(["крестики"]))
@flags.throttling_key('default')
async def start_game(message: Message):
    if message.chat.type == 'private':
        await message.reply("❌ Игра доступна только ответом на сообщение")
    else:
        chat_id = message.chat.id
        if chat_id in games:
            game = games.get(message.chat.id)
            if time.time() - game.time < 300:
                xd = int(time.time() - game.time)

                return await message.reply(f"❕ В данном чате уже идет игра ! {timetostr(300 - xd)}")
            games.pop(chat_id)
        if message.reply_to_message:
            if message.reply_to_message.from_user.id == message.from_user.id:
                return await message.reply("❌ Одиночка найди себе другого игрока!")
            query1 = f'SELECT reg_date FROM users WHERE id={message.reply_to_message.from_user.id}'
            sql.get_cursor().execute(query1)
            member = sql.get_cursor().fetchone()
            if member != None:
                await message.reply("🧩 Вы отправили запрос на участье в игру крестики-нолики !",
                                    reply_markup=tictac(user_id1=message.from_user.id,
                                                        user_id2=message.reply_to_message.from_user.id).as_markup())
            else:
                await message.reply("❌ Игрок не зарегестрирован в боте")


@flags.throttling_key('default')
async def join_game(callback_query: CallbackQuery):
    action, user1, user2 = callback_query.data.split(':')
    if action == 'tic_accept' and int(user2) == callback_query.from_user.id:
        chat_id = callback_query.message.chat.id
        if chat_id in games:
            game = games.get(callback_query.message.chat.id)
            if time.time() - game.time < 300:
                xd = int(time.time() - game.time)
                return await callback_query.message.edit_text(f"❕ В данном чате уже идет игра !\n"
                                                              f"Новую игру можно начать через: {timetostr(300 - xd)}")
            games.pop(chat_id)
        games[chat_id] = TicTacToe(user1, user2, time.time(), callback_query.message.message_id)
        game = games.get(callback_query.message.chat.id)
        keyboard = InlineKeyboardBuilder()
        for row in range(5):
            row_keyboard = []
            for col in range(5):
                if row == 0 or col == 0 or col == 4 or row == 4:
                    button = InlineKeyboardButton(text='⬜', callback_data=f"tictac_{row} {col}")
                else:
                    button = InlineKeyboardButton(text=game.board[row][col], callback_data=f"tictac_{row} {col}")
                row_keyboard.append(button)
            keyboard.row(*row_keyboard)
        player1 = User(id=user1)
        player2 = User(id=user2)
        await callback_query.message.edit_text(text=f'1️⃣.Игрок: {player1.link}[❌]\n'
                                                    f'2️⃣.Игрок: {player2.link}[⭕]\n'
                                                    f'➖➖➖➖➖➖➖➖➖➖➖➖\n'
                                                    f"🧩 Ход: {player1.link} [{'❌' if game.turn == game.player1 else '⭕'}]",
                                               reply_markup=keyboard.as_markup(), disable_web_page_preview=True)
    elif int(user2) == callback_query.from_user.id:
        await callback_query.message.edit_text("❌ Игрок отказался от игры")
    else:
        await callback_query.answer("❌ Не трожь не твое")
