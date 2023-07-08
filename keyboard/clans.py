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


def war_clan_info(clan_id):
    clanwar_kb = InlineKeyboardBuilder()
    clanwar_kb.add(
        InlineKeyboardButton(text='⚔ Информация', callback_data=f'clanwar:info:{clan_id}'))
    return clanwar_kb.as_markup()


def war_clan_member(clan_id):
    clanwar_kb = InlineKeyboardBuilder()
    clanwar_kb.add(
        InlineKeyboardButton(text='👥 Участники', callback_data=f'clanwar:member:{clan_id}'))
    return clanwar_kb.as_markup()


def war_clan(clan_id):
    clanwar_kb = InlineKeyboardBuilder()
    clanwar_kb.add(
        InlineKeyboardButton(text='👥 Участники', callback_data=f'clanwar:member:{clan_id}'))
    clanwar_kb.add(
        InlineKeyboardButton(text='⚔ В бой', callback_data=f'clanwar:attack:{clan_id}'))
    return clanwar_kb.adjust(1).as_markup()
