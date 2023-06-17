import time

from aiogram import flags

from config import bot_name
from keyboard.generate import show_business_kb, show_balance_kb, buy_business_kb, business_kb
from aiogram.types import Message

from utils.main.cash import to_str, get_cash
from utils.main.businesses import Business, businesses
from utils.main.db import sql

from filters.users import flood_handler

numbers_emoji = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']


@flags.throttling_key('default')
async def businesses_list_handler(message: Message):
    text = 'Название - цена - доход - налог\n'
    asd = sql.execute(f'SELECT sell_count FROM users WHERE id = {message.from_user.id}', False, True)[0][0]
    if asd is None:
        asd = 0
    xa = asd = float(f'0.{asd}')
    for index, i in businesses.items():
        emoji = ''.join(numbers_emoji[int(i)] for i in str(index))
        price = i["price"] - int(i["price"] * xa)
        text += f'<code>{emoji}</code>. {i["name"]} - {to_str(price)} - {to_str(i["doxod"])}' \
                f' - {to_str(i["nalog"])}\n'
    return await message.reply(
        f'<i>(Ваша скидка: x{asd})</i>\n\n'
        + text + '\n\nИспользуйте: <code>Биз купить (номер)</code> чтобы купить!',
        reply_markup=buy_business_kb.as_markup())


@flags.throttling_key('default')
async def business_handler(message: Message):
    flood = await flood_handler(message)
    if flood:
        arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[
            0].lower() else message.text.split()[2:]
        try:
            business = Business(user_id=message.from_user.id)
        except:
            business = None
            if len(arg) < 1 or arg[0].lower() != 'купить':
                return await businesses_list_handler(message)
            try:
                if not arg[1].isdigit():
                    return await businesses_list_handler(message)
            except:
                return await businesses_list_handler(message)
        if len(arg) == 0:
            return await message.reply(text=business.text, reply_markup=business_kb.as_markup())
        elif arg[0].lower() in ['список', 'лист']:
            return await businesses_list_handler(message)
        elif arg[0].lower() == 'продать':
            doxod = business.sell()
            sql.execute(f'UPDATE users SET bank = bank + {doxod} WHERE id = {message.from_user.id}', True, False)
            await message.reply(f'✅ Вы продали бизнес и с учётом налогов, и дохода вы получили: {to_str(doxod)}',
                                reply_markup=show_balance_kb.as_markup())

            return
        elif arg[0].lower() == 'купить':

            if business:
                return await message.reply('❗ У вас уже есть бизнес, можно иметь только 1.',
                                           reply_markup=show_business_kb.as_markup())
            try:
                i = businesses[int(arg[1])]
            except:
                return await message.reply('❌ Ошибка. Неверный номер бизнеса! 1-6')

            xa = sql.execute(f'SELECT sell_count, balance FROM users WHERE id = {message.from_user.id}', False, True)[0]
            balance = xa[1]
            xa = xa[0]
            if xa is None:
                xa = 0
            xa = float(f'0.{xa}')
            price = i["price"] - int(i["price"] * xa)

            if balance < price:
                return await message.reply(
                    f'💲 На руках недостаточно денег для покупки, нужно: {to_str(price)}',
                    reply_markup=show_balance_kb.as_markup())

            Business.create(user_id=message.from_user.id, business_index=int(arg[1]))
            sql.execute(f'UPDATE users SET balance = balance - {price}, sell_count = 0 WHERE id ='
                        f' {message.from_user.id}', True)
            await message.reply(f'✅ Вы успешно приобрели бизнес {i["name"]} за {to_str(price)}',
                                reply_markup=show_business_kb.as_markup())

            return
        elif arg[0].lower() in ['закрыть', 'открыть']:
            business.editmany(arenda=not business.arenda, last=time.time() if (not business.arenda) is True else None)
            await message.reply('🔓 Вы открыли свой бизнес!' if business.arenda else
                                '🔒 Вы закрыли свой бизнес!',
                                reply_markup=show_business_kb.as_markup())

            return
        elif arg[0].lower() in ['снять', 'доход']:
            xd = business.cash
            if len(arg) > 1:
                try:
                    xd = get_cash(arg[1])
                except:
                    pass
            if business.cash < xd or business.cash < 0:
                return await message.reply('💲 Недостаточно денег на счету бизнеса!',
                                           reply_markup=show_balance_kb.as_markup())
            elif xd <= 0:
                return await message.reply('❌ Нельзя так!')
            sql.executescript(f'''UPDATE users SET bank = bank + {xd} WHERE id = {message.from_user.id};
            UPDATE businesses SET cash = {business.cash - xd} WHERE owner = {business.owner};''', True)

            await message.reply(f'✅ Вы успешно сняли {to_str(business.cash)} с прибыли бизнеса!',
                                reply_markup=show_balance_kb.as_markup())

            return
        elif arg[0].lower() in ['налог', 'налоги']:
            xd = business.nalog
            if len(arg) > 1:
                try:
                    xd = get_cash(arg[1])
                except:
                    pass
            if business.nalog < 1:
                return await message.reply('💲 Налог на бизнес и так оплачен!',
                                           reply_markup=show_business_kb.as_markup())
            elif business.nalog < xd:
                xd = business.nalog
            elif xd <= 0:
                return await message.reply('❌ Нельзя так!')
            if sql.execute(f'SELECT bank FROM users WHERE id = {message.from_user.id}', False, True)[0][0] < xd:
                return await message.reply(f'💲 Недостаточно денег в банке для оплаты налога, нужно: {to_str(xd)}!',
                                           reply_markup=show_balance_kb.as_markup())

            sql.executescript(f'''UPDATE users SET bank = bank - {xd} WHERE id = {message.from_user.id};
                    UPDATE businesses SET nalog = {business.nalog - xd} WHERE owner = {business.owner};''', True)

            await message.reply('✅ Налог на бизнес успешно оплачен!', reply_markup=show_business_kb.as_markup())

            return
        else:
            return await message.reply('❌ Ошибка. Используйте: <code>Бизнес (снять\сдать\оплатить) (сумма)</code>')
