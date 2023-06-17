from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

marrye_kb = InlineKeyboardBuilder()
marrye_kb.add(InlineKeyboardButton(text='💲 Снять', switch_inline_query_current_chat='Семья снять '))
marrye_kb.add(InlineKeyboardButton(text='💸 Положить', switch_inline_query_current_chat='Семья положить '))
marrye_kb.add(InlineKeyboardButton(text='🆙 Улучшить', switch_inline_query_current_chat='Семья улучшить'))
marrye_kb.add(InlineKeyboardButton(text='❌ Удалить', switch_inline_query_current_chat='Семья выйти'))
marrye_kb.adjust(2)
