from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

euro_kb = InlineKeyboardBuilder()
euro_kb.add(InlineKeyboardButton(text='💶 Купить', switch_inline_query_current_chat='Евро купить '))
euro_kb.add(InlineKeyboardButton(text='🪝 Продать', switch_inline_query_current_chat='Евро продать '))
euro_kb.add(InlineKeyboardButton(text='🥫 Улучшить', switch_inline_query_current_chat='Евро улучшить '))
euro_kb.adjust(2)

my_euro_kb = InlineKeyboardBuilder()
my_euro_kb.add(InlineKeyboardButton(text='💶 Моя Кладовка', switch_inline_query_current_chat='Евро'))

uah_kb = InlineKeyboardBuilder()
uah_kb.add(InlineKeyboardButton(text='💶 Купить', switch_inline_query_current_chat='Юань купить '))
uah_kb.add(InlineKeyboardButton(text='🪝 Продать', switch_inline_query_current_chat='Юань продать '))
uah_kb.add(InlineKeyboardButton(text='🥫 Улучшить', switch_inline_query_current_chat='Юань улучшить '))
uah_kb.adjust(2)

my_uah_kb = InlineKeyboardBuilder()
my_uah_kb.add(InlineKeyboardButton(text='💴 Моя Кладовка', switch_inline_query_current_chat='Юань'))
