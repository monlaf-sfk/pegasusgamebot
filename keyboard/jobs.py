from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

jobs_kb = InlineKeyboardBuilder()
jobs_kb.add(InlineKeyboardButton(text='💸 Дать взятку', switch_inline_query_current_chat='Работа взятка'))
jobs_kb.add(InlineKeyboardButton(text='💪🏿 Устроиться', switch_inline_query_current_chat='Работа устроиться '))
jobs_kb.adjust(1)
rabotat_kb = InlineKeyboardBuilder()
rabotat_kb.add(InlineKeyboardButton(text='💪🏿 Работать', switch_inline_query_current_chat='Фабрика работать'))

shaxta_kb = InlineKeyboardBuilder()
shaxta_kb.add(InlineKeyboardButton(text='💪🏿 Копать', switch_inline_query_current_chat='Шахта копать'))

report_kb = InlineKeyboardBuilder()
report_kb.add(InlineKeyboardButton(text='🆘 Рассказать о баге', url='https://t.me/corching'))
