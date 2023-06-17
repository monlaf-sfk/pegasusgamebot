import time

from aiogram import flags
from aiogram.types import Message

import config
from config import bot_name
from utils.logs import writelog
from utils.main.cash import to_str, get_cash
from utils.main.users import User
from filters.users import flood_handler


@flags.throttling_key('default')
async def deposit_handler(message: Message):
    flood = await flood_handler(message)
    if flood:
        spliy = message.text.split() if not bot_name.lower() in message.text.split()[
            0].lower() else message.text.split()[1:]
        user = User(user=message.from_user)
        try:
            arg = abs(get_cash(spliy[2].lower().replace('всё', str(user.deposit)).replace('все', str(user.deposit)))) if \
            spliy[
                1].lower() in [
                'снять',
                'вывести',
                'обналичить'] else abs(
                get_cash(
                    spliy[2].lower().replace('всё', str(user.balance)).replace('все', str(user.balance))))
            if arg <= 0:
                raise Exception(123)
        except:
            return await message.reply(
                f'❌ Ошибка! Неверный аргумент, введите: <code>депозит (снять\пополнить\вывести) {{ '
                f'сумма }}</code>')
        if spliy[1].lower() in ['положить', 'пополнить']:
            if user.balance < arg:
                return await message.reply('💸 На руках недостаточно средств, чтобы пополнить такую сумму на депозит!')
            donate = 5_000_000
            if user.donate:
                if user.donate.id > 3:
                    user.editmany(balance=user.balance - arg, deposit=user.deposit + arg, deposit_date=time.time())
                    await writelog(message.from_user.id, f'Депозит +{to_str(arg)}')
                    return await message.reply(
                        f'✅ Вы пополнили баланс депозита на +{to_str(arg)}, текущий баланс на депозите: 'f'{to_str(user.deposit)}')
                item = config.donates[user.donate.id]
                donate = item['limit_dep']

            if donate < user.deposit + arg:
                return await message.reply(
                    '💸 Вы превысили лимит депозита!\n🔎 Увеличить лимит можно с помощью покупки доната "Донат"!')
            user.editmany(balance=user.balance - arg, deposit=user.deposit + arg, deposit_date=time.time())
            await message.reply(f'✅ Вы пополнили баланс депозита на +{to_str(arg)}, текущий баланс на депозите: '
                                f'{to_str(user.deposit)}')
            await writelog(message.from_user.id, f'Депозит +{to_str(arg)}')
            return
        elif spliy[1].lower() in ['снять', 'вывести']:
            if user.deposit < arg:
                return await message.reply('💶 На депозите недостаточно средств, чтобы снять средства!')
            user.editmany(balance=user.balance + arg, deposit=user.deposit - arg, deposit_date=time.time())
            await message.reply(f'✅ Вы сняли средства в размере {to_str(arg)} и теперь у вас на руках '
                                f'{to_str(user.balance)}')
            await writelog(message.from_user.id, f'Депозит -{to_str(arg)}')
            return
        return await message.reply(f'❌ Ошибка! Неверный аргумент, введите: <code>депозит (снять\пополнить\вывести) '
                                   f'(сумма)</code>')
