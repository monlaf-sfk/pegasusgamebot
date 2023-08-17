from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from handlers.users.games.blackjack.help_func import get_card_value
from utils.main.cash import transform
from utils.main.users import User


class GameBlackjackCallback(CallbackData, prefix="game"):
    action: str
    id: int
    game_id: str


class NewGameCallbackBlackjack(CallbackData, prefix="newgame"):
    action: str
    id: int
    as_separate: bool
    summ: int


class BlackjackGame(StatesGroup):
    waiting_for_start = State()
    waiting_for_action = State()
    waiting_for_action2 = State()
    waiting_for_action3 = State()


def to_str3(money: int):
    b = f'{money:,}'
    return f"{b.replace(',', '.')}$"


def newgame_black_kb(user_id: int, summ: int = 0) -> InlineKeyboardMarkup:
    if summ == 0:
        keyboard = InlineKeyboardBuilder()
        user = User(id=user_id)

        if user.balance >= 10:
            keyboard.add(
                InlineKeyboardButton(text=f"💰 Играть на {transform(round(user.balance / 2))}$",
                                     callback_data=NewGameCallbackBlackjack(action="new_game", id=f'{user_id}',
                                                                            as_separate=True,
                                                                            summ=round(user.balance / 2)).pack())
            )
            keyboard.add(
                InlineKeyboardButton(text=f"💰 Играть на {transform(round(user.balance / 3))}$",
                                     callback_data=NewGameCallbackBlackjack(action="new_game", id=f'{user_id}',
                                                                            as_separate=True,
                                                                            summ=round(user.balance / 3)).pack())
            )
            keyboard.add(
                InlineKeyboardButton(text=f"💰 Ва-банк",
                                     callback_data=NewGameCallbackBlackjack(action="new_game", id=f'{user_id}',
                                                                            as_separate=True,
                                                                            summ=user.balance).pack())
            )
            return keyboard.adjust(2).as_markup()
        else:
            keyboard.add(
                InlineKeyboardButton(text=f"💰 Ва-банк",
                                     callback_data=NewGameCallbackBlackjack(action="new_game", id=f'{user_id}',
                                                                            as_separate=True,
                                                                            summ=user.balance).pack())
            )
            return keyboard.adjust(2).as_markup()

    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text=f"🔄 Играть на {to_str3(summ)}",
                             callback_data=NewGameCallbackBlackjack(action="new_game", id=f'{user_id}',
                                                                    as_separate=True, summ=summ).pack())
    )
    return keyboard.as_markup()


def replay_game_black_kb(user_id: int, summ: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text=f"🔄 Играть заново на {to_str3(summ)}",
                             callback_data=NewGameCallbackBlackjack(action="new_game", id=f'{user_id}',
                                                                    as_separate=True, summ=summ).pack())
    )
    return keyboard.as_markup()


def game_blackjack_kb(game_id: str, user_id: int, player_hand: list = None, dealer_hand: list = None,
                      split: bool = False) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    if split:
        keyboard.add(
            InlineKeyboardButton(text="➕ Ещё",
                                 callback_data=GameBlackjackCallback(action="hit", id=f'{user_id}',
                                                                     game_id=game_id).pack()),
            InlineKeyboardButton(text="❌ Стоп",
                                 callback_data=GameBlackjackCallback(action="stand", id=f'{user_id}',
                                                                     game_id=game_id).pack()),

        )
        return keyboard.adjust(2).as_markup()
    else:
        if player_hand and len(player_hand) == 2:

            keyboard.add(
                InlineKeyboardButton(text="➕ Ещё",
                                     callback_data=GameBlackjackCallback(action="hit", id=f'{user_id}',
                                                                         game_id=game_id).pack()),
                InlineKeyboardButton(text="❌ Стоп",
                                     callback_data=GameBlackjackCallback(action="stand", id=f'{user_id}',
                                                                         game_id=game_id).pack()),
                InlineKeyboardButton(text="💰 Удвоить",
                                     callback_data=GameBlackjackCallback(action="double", id=f'{user_id}',
                                                                         game_id=game_id).pack()),
                InlineKeyboardButton(text="🚫 Отказ",
                                     callback_data=GameBlackjackCallback(action="surrender", id=f'{user_id}',
                                                                         game_id=game_id).pack()),
            )
            if dealer_hand and len(dealer_hand) == 1 and get_card_value(dealer_hand[0]) == 11:
                keyboard.add(
                    InlineKeyboardButton(text="❤ Страховка",
                                         callback_data=GameBlackjackCallback(action="insurance", id=f'{user_id}',
                                                                             game_id=game_id).pack()),
                )
        else:
            keyboard.add(
                InlineKeyboardButton(text="➕ Ещё",
                                     callback_data=GameBlackjackCallback(action="hit", id=f'{user_id}',
                                                                         game_id=game_id).pack()),
                InlineKeyboardButton(text="❌ Стоп",
                                     callback_data=GameBlackjackCallback(action="stand", id=f'{user_id}',
                                                                         game_id=game_id).pack())
            )
        return keyboard.adjust(2).as_markup()


def game_blackjacksplit_kb(game_id: str, user_id: int, dealer_hand: list = None) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.add(
        InlineKeyboardButton(text="➕ Ещё",
                             callback_data=GameBlackjackCallback(action="hit", id=f'{user_id}',
                                                                 game_id=game_id).pack()),
        InlineKeyboardButton(text="❌ Стоп",
                             callback_data=GameBlackjackCallback(action="stand", id=f'{user_id}',
                                                                 game_id=game_id).pack()),
        InlineKeyboardButton(text="💰 Удвоить",
                             callback_data=GameBlackjackCallback(action="double", id=f'{user_id}',
                                                                 game_id=game_id).pack()),
        InlineKeyboardButton(text="↔ Разделить",
                             callback_data=GameBlackjackCallback(action="split", id=f'{user_id}',
                                                                 game_id=game_id).pack()),
        InlineKeyboardButton(text="🚫 Отказ",
                             callback_data=GameBlackjackCallback(action="surrender ", id=f'{user_id}',
                                                                 game_id=game_id).pack()),
    )
    if dealer_hand and len(dealer_hand) == 1 and get_card_value(dealer_hand[0]) == 11:
        keyboard.add(
            InlineKeyboardButton(text="❤ Страховка",
                                 callback_data=GameBlackjackCallback(action="insurance", id=f'{user_id}',
                                                                     game_id=game_id).pack()),
        )
        return keyboard.adjust(3).as_markup()
    return keyboard.adjust(2).as_markup()


def game_blackjack_insurance_kb(game_id: str, user_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="➕ Ещё",
                             callback_data=GameBlackjackCallback(action="hit", id=f'{user_id}',
                                                                 game_id=game_id).pack()),
        InlineKeyboardButton(text="❌ Стоп",
                             callback_data=GameBlackjackCallback(action="stand", id=f'{user_id}',
                                                                 game_id=game_id).pack()),
        InlineKeyboardButton(text="💰 Удвоить",
                             callback_data=GameBlackjackCallback(action="double", id=f'{user_id}',
                                                                 game_id=game_id).pack()),

    )
    return keyboard.adjust(2).as_markup()
