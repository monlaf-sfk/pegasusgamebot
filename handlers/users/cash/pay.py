from aiogram import flags
from aiogram.types import Message

from config import bot_name
from keyboard.generate import show_balance_kb
from utils.logs import writelog
from utils.main.cash import to_str, get_cash
from utils.main.users import User
from filters.users import flood_handler


@flags.throttling_key('default')
async def pay_handler(message: Message):
    flood = await flood_handler(message)
    if flood:
        arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[
            0].lower() else message.text.split()[2:]
        if len(arg) == 0:
            return await message.reply(
                '❌ Ошибка. Используйте: <code>(передать/дать) (<i>сумма</i>) <b>{username\id}</b></code>')
        user = User(user=message.from_user)
        if user.payban:
            return await message.reply('❌ На ваш аккаунт наложено ограничение на переводы !')
        try:
            summ = abs(get_cash(arg[0].lower().replace('всё', str(user.balance)).replace('все', str(user.balance))))
            if summ <= 0:
                raise Exception('123')
        except:
            return await message.reply('❌ Ошибка. Неверно введена сумма!')
        if len(arg) == 2 and '@' not in arg[1]:
            return await message.reply('❌ Ошибка. Вы не указали кому передать деньги!')
        elif len(arg) == 1 and not message.reply_to_message:
            return await message.reply('❌ Ошибка. Вы не ответили на сообщение кому передать деньги!')
        elif len(arg) == 2:
            try:
                to_user = User(username=arg[1].replace('@', ''))
            except:
                return await message.reply(f'❌ Ошибка. Пользователя <code>{arg[1]}</code> не существует!',
                                           disable_web_page_preview=True)
        elif message.reply_to_message:
            to_user = User(user=message.reply_to_message.from_user)
        else:
            return await message.reply(
                '❌ Ошибка. Используйте: <code>(передать/дать) (<i>сумма</i>) <b>{username\id}</b></code>')

        if user.id == to_user.id:
            return await message.reply('❌ Ошибка. Самому себе нельзя передать предмет!')
        if to_user.payban:
            return await message.reply('❌ У данного аккаунта ограничение на переводы !')
        if user.balance < summ:
            return await message.reply('❌ Ошибка. Недостаточно денег на руках! 💸',
                                       reply_markup=show_balance_kb.as_markup())
        to_user.edit('balance', to_user.balance + summ)
        user.edit('balance', user.balance - summ)
        await message.reply(f'✅ Вы успешно передали {to_str(summ)} пользователю {to_user.link}',
                            disable_web_page_preview=True,
                            reply_markup=show_balance_kb.as_markup())
        await writelog(message.from_user.id, f'Передача {to_str(summ)} юзеру {to_user.link}')
        return
