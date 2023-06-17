from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

buy_case_kb = InlineKeyboardBuilder()
buy_case_kb.add(InlineKeyboardButton(text='🛒 Купить кейс', switch_inline_query_current_chat='Кейс купить '))

open_case_kb = InlineKeyboardBuilder()
open_case_kb.add(InlineKeyboardButton(text='📦 Открыть кейс', switch_inline_query_current_chat='Кейс открыть '))

play_spin_kb = InlineKeyboardBuilder()
play_spin_kb.add(InlineKeyboardButton(text='🎰 Играть ещё', switch_inline_query_current_chat='Спин '))

play_dice_kb = InlineKeyboardBuilder()
play_dice_kb.add(InlineKeyboardButton(text='🎲 Играть ещё', switch_inline_query_current_chat='Кубик '))

play_bowling_kb = InlineKeyboardBuilder()
play_bowling_kb.add(InlineKeyboardButton(text='🎳 Играть ещё', switch_inline_query_current_chat='Боулинг '))

play_basketball_kb = InlineKeyboardBuilder()
play_basketball_kb.add(InlineKeyboardButton(text='🏀️ Играть ещё', switch_inline_query_current_chat='Баскетбол '))

play_darts_kb = InlineKeyboardBuilder()
play_darts_kb.add(InlineKeyboardButton(text='🎯 Играть ещё', switch_inline_query_current_chat='Дартс '))

play_footbal_kb = InlineKeyboardBuilder()
play_footbal_kb.add(InlineKeyboardButton(text='⚽ Играть ещё', switch_inline_query_current_chat='Футбол '))

play_casino_kb = InlineKeyboardBuilder()
play_casino_kb.add(InlineKeyboardButton(text='♣ Играть ещё', switch_inline_query_current_chat='Казино '))


def tictac(user_id1, user_id2):
    gamestavka = InlineKeyboardBuilder()
    gamestavka.add(InlineKeyboardButton(text='✅ Согласиться', callback_data=f'tic_accept:{user_id1}:{user_id2}'))
    gamestavka.add(InlineKeyboardButton(text='❌ Отказаться', callback_data=f'tic_decline:{user_id1}:{user_id2}'))
    gamestavka.adjust(1)
    return gamestavka


def to_str3(money: int):
    b = f'{money:,}'
    return f"{b.replace(',', '.')}$"


def ruletka(user_id, state, sum):
    ruletka_kb = InlineKeyboardBuilder()
    ruletka_kb.add(InlineKeyboardButton(text='🔫  Выстрелить', callback_data=f'ruletc:{user_id}:{state}:{sum}'))
    ruletka_kb.add(InlineKeyboardButton(text='💸 Стоп', callback_data=f'rulets:{user_id}:{state}:{sum}'))
    ruletka_kb.adjust(2)
    return ruletka_kb


def ruletka2(user_id, state, sum):
    ruletka_kb1 = InlineKeyboardBuilder()
    ruletka_kb1.add(InlineKeyboardButton(text=f'🔫  Заново на {to_str3(sum)}',
                                         callback_data=f'return_ruletka:{user_id}:{state}:{sum}'))
    return ruletka_kb1
