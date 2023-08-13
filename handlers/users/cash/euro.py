from aiogram import flags
from aiogram.types import Message

from config import bot_name
from keyboard.generate import show_balance_kb
from keyboard.cash import euro_kb, my_euro_kb
from utils.logs import writelog
from utils.main.cash import get_cash, to_str
from utils.main.db import sql
from utils.main.euro import Euro, euro_to_usd
from filters.users import flood_handler


@flags.throttling_key('default')
async def euro_handler(message: Message):
    flood = await flood_handler(message)
    if flood:
        arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[
            0].lower() else message.text.split()[2:]
        euro = Euro(owner=message.from_user.id)

        if len(arg) == 0:
            return await message.reply(euro.text, reply_markup=euro_kb.as_markup())
        elif arg[0].lower() in ['купить']:
            if len(arg) < 2:
                return await message.reply('❌ Используйте: <code>Евро купить (кол-во)</code>',
                                           reply_markup=my_euro_kb.as_markup())
            try:
                xa = sql.execute(f'SELECT bank FROM users WHERE id = {message.from_user.id}', False, True)[0][0]
                summ = get_cash(arg[1]) if arg[1].lower() not in ['всё', 'все'] else int(xa / euro_to_usd(1))
                if summ <= 0:
                    raise Exception('123')
            except:
                return await message.reply('🚫 Неверный ввод!')
            if (summ + euro.balance) > euro.spaciousness:
                return await message.reply('🚫 Вы превысили лимит вашей Кладовки!')
            user_summ = euro_to_usd(summ)

            if user_summ > xa:
                text = f'❌ Недостаточно денег на руках, нужно: {to_str(user_summ)}'
                if len(text) > 4095:
                    return await message.reply(f'❌ Недостаточно денег на руках\n♾ Нужно: Очень много денег!',
                                               reply_markup=show_balance_kb.as_markup())
                return await message.reply(text,
                                           reply_markup=show_balance_kb.as_markup())

            sql.executescript(f'UPDATE euro SET balance = balance + {summ} WHERE owner = {message.from_user.id};\n'
                              f'UPDATE users SET bank = bank - {user_summ} WHERE id = {message.from_user.id};',
                              True, False)

            await message.reply(f'✅ Вы успешно приобрели {summ} евро за {to_str(user_summ)}',
                                reply_markup=my_euro_kb.as_markup())
            await writelog(message.from_user.id, f'евро +{summ} за {to_str(user_summ)}')
            # now = euro_price() + int(summ * random.choice([0.01, 0.05, 0.04, 0.03, 0]))

            # await set_euro_price(now)

            return

        elif arg[0].lower() in ['продать', 'снять']:
            try:
                if arg[1].isdigit():
                    summ = get_cash(arg[1])
                else:
                    raise Exception('123')
            except:
                summ = euro.balance
            if summ <= 0:
                return await message.reply('😴 Кол-во EURO меньше или равно нулю!')
            elif summ > euro.balance:
                return await message.reply('😴 Кол-во EURO больше чем баланс Кладовки!')

            # now = euro_price() - int(summ * 0.0005)

            # await set_euro_price(now)

            user_summ = euro_to_usd(summ)

            sql.executescript(f'UPDATE euro SET balance = balance - {summ} WHERE owner = {message.from_user.id};\n'
                              f'UPDATE users SET bank = bank + {user_summ} WHERE id = {message.from_user.id};',
                              True, False)

            await message.reply(f'✅ Вы успешно сняли {to_str(user_summ)} с Кладовки!')
            await writelog(message.from_user.id, f'евро -{summ} за {to_str(user_summ)}')
            return

        elif arg[0].lower() in ['улучш', 'улучшить']:
            xa = sql.execute(f'SELECT bank FROM users WHERE id = {message.from_user.id}', False, True)[0][0]
            price = 100000 * euro.level
            if xa < price:
                return await message.reply(f'🚫 Недостаточно денег в банке для улучшения, нужно: {to_str(price)}',
                                           reply_markup=my_euro_kb.as_markup())

            sql.executescript(f'UPDATE users SET bank = bank - {price} WHERE id = {message.from_user.id};\n'
                              f'UPDATE euro SET level = level + 1 WHERE owner = {message.from_user.id};')
            return await message.reply(f'🥫 Вы улучшили свою Кладовку EURO и теперь он вмещает: '
                                       f'{to_str((euro.level + 1) * 1000)}',
                                       reply_markup=my_euro_kb.as_markup())
