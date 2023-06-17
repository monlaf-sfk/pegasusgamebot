from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def member_kb(clan_id):
    help_kb = InlineKeyboardBuilder()
    help_kb.add(InlineKeyboardButton(text='👥 Участники', callback_data=f'members_{clan_id}'))
    return help_kb


def info_clan(user2, user1, status):
    info_clan_kb = InlineKeyboardBuilder()
    info_clan_kb.add(
        InlineKeyboardButton(text='⛔ Кик', callback_data=f'claninfo_k:{user2}:{user1}'))
    if status == 0:
        info_clan_kb.add(
            InlineKeyboardButton(text='⬆️ Повысить', callback_data=f'claninfo_up:{user2}:{user1}'))
    elif status == 1:
        info_clan_kb.add(
            InlineKeyboardButton(text='⬇️ Понизить', callback_data=f'claninfo_dow:{user2}:{user1}'))
    return info_clan_kb
