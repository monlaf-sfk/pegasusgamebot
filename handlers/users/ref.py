from contextlib import suppress

from aiogram import flags
from aiogram.exceptions import TelegramForbiddenError
from aiogram.types import Message

from config import bot_name

from keyboard.main import check_ls_kb, ref_share_func
from loader import bot

from utils.main.cash import to_str
from utils.main.db import sql
from utils.main.users import User


@flags.throttling_key('default')
async def refferal_handler(message: Message):
    user = User(user=message.from_user)
    zarefa = sql.execute("SELECT zarefa FROM other", commit=False, fetch=True)[0][0]
    if user.id == message.chat.id:
        return await message.reply(f'✨ Реферальная система бота @{bot_name}\n'
                                   f'➖➖➖➖➖➖➖➖➖➖➖➖\n'
                                   f'🔗 Ваша персональная ссылка: https://t.me/{bot_name}?start={user.id}\n'
                                   f'» Если по ней перейдет человек, не игравший в бота, ты заработаешь игровую валюту\n\n'
                                   f'🎁 Ежедневно ты можешь забрать бонус за приведенных игроков\n'
                                   f'➖➖➖➖➖➖➖➖➖➖➖➖\n'
                                   f'💰 Приглашенный пользователь и Ты получат {to_str(zarefa)}\n'
                                   f'👥 Кол-во приглашённых людей: <b>{user.refs}</b>', disable_web_page_preview=True,
                                   reply_markup=ref_share_func(user.id).as_markup())
    else:
        with suppress(TelegramForbiddenError):
            await bot.send_message(text=f'✨ Реферальная система бота @{bot_name}\n'
                                        f'➖➖➖➖➖➖➖➖➖➖➖➖\n'
                                        f'🔗 Ваша персональная ссылка: https://t.me/{bot_name}?start={user.id}\n'
                                        f'» Если по ней перейдет человек, не игравший в бота, ты заработаешь игровую валюту\n\n'
                                        f'🎁 Ежедневно ты можешь забрать бонус за приведенных игроков\n'
                                        f'➖➖➖➖➖➖➖➖➖➖➖➖\n'
                                        f'💰 Приглашенный пользователь и Ты получат {to_str(zarefa)}\n'
                                        f'👥 Кол-во приглашённых людей: <b>{user.refs}</b>',
                                   disable_web_page_preview=True, chat_id=user.id,
                                   reply_markup=ref_share_func(user.id).as_markup())
            return await message.reply('👥 Реф-Меню было отправлено в личку с ботом!',
                                       reply_markup=check_ls_kb.as_markup())

        return await message.reply('🙃 Вы никогда не писали боту в лс, я не могу отправить вам реф-меню',
                                   reply_markup=check_ls_kb.as_markup())
