from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def help_keyboard(user_id):
    help_kb = InlineKeyboardBuilder()
    help_kb.add(InlineKeyboardButton(text='Ⓜ', callback_data=f'help_main:{user_id}'))
    help_kb.add(InlineKeyboardButton(text='⚔️', callback_data=f'help_clan:{user_id}'))
    help_kb.add(InlineKeyboardButton(text='🎮', callback_data=f'help_games:{user_id}'))
    help_kb.add(InlineKeyboardButton(text='💫', callback_data=f'help_unik:{user_id}'))
    help_kb.add(InlineKeyboardButton(text='🛠️', callback_data=f'help_work:{user_id}'))
    help_kb.add(InlineKeyboardButton(text='🏙', callback_data=f'help_city:{user_id}'))
    help_kb.add(InlineKeyboardButton(text='🚙', callback_data=f'help_imush:{user_id}'))
    help_kb.add(InlineKeyboardButton(text='🗂️', callback_data=f'help_other:{user_id}'))
    help_kb.adjust(2)
    return help_kb


def back_help_keyboard(user_id):
    back_kb = InlineKeyboardBuilder()
    back_kb.add(InlineKeyboardButton(text='🔙 Назад', callback_data=f'help_back:{user_id}'))
    return back_kb


donate_help_kb = InlineKeyboardBuilder()
donate_help_kb.add(InlineKeyboardButton(text='1️⃣', callback_data='priv_vip'))
donate_help_kb.add(InlineKeyboardButton(text='3️⃣', callback_data='priv_premium'))
donate_help_kb.add(InlineKeyboardButton(text='2️⃣', callback_data='priv_beta'))
donate_help_kb.add(InlineKeyboardButton(text='4️⃣', callback_data='priv_elite'))
donate_help_kb.add(InlineKeyboardButton(text='5️⃣', callback_data=f'priv_admin'))
donate_help_kb.add(InlineKeyboardButton(text='6️⃣', callback_data=f'priv_subject'))
donate_help_kb.add(InlineKeyboardButton(text='🎄 Получить коины', switch_inline_query_current_chat="задонатить"))
donate_help_kb.adjust(2)

donate_back_kb = InlineKeyboardBuilder()
donate_back_kb.add(InlineKeyboardButton(text='🔙 Назад', callback_data='priv_back'))
