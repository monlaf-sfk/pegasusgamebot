from datetime import datetime

from aiogram import flags
from aiogram.types import Message

from config import bot_name
from keyboard.generate import show_balance_kb, show_inv_kb, show_yaxta_kb, yaxta_kb, buy_yaxta_kb, ride_yaxta_kb

from utils.main.yaxti import yaxti, Yaxta
from utils.main.cash import to_str, get_cash
from utils.main.db import sql
from filters.users import flood_handler

numbers_emoji = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']


@flags.throttling_key('default')
async def yaxti_list_handler(message: Message):
    text = '⛵️ Список Яхт:\n'
    asd = sql.execute(f'SELECT sell_count FROM users WHERE id = {message.from_user.id}', False, True)[0][0]
    if asd is None:
        asd = 0
    xa = float(f'0.{asd}')
    for index, i in yaxti.items():
        emoji = ''.join(numbers_emoji[int(i)] for i in str(index))
        price = i["price"] - int(i["price"] * xa)
        text += f'<code>{emoji}</code>.{i["name"]}\n' \
                f'💵 Цена: {to_str(price)} \n' \
                f'💲 Налог: {to_str(i["nalog"])}\n\n'
    return await message.reply(
        f'<i>(Ваша скидка: x{asd})</i>\n'
        + text + '\n\nИспользуйте: <code>Яхта купить (номер)</code> чтобы купить!',
        reply_markup=buy_yaxta_kb.as_markup())


@flags.throttling_key('default')
async def yaxti_handler(message: Message):
    flood = await flood_handler(message)
    if flood:
        arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[
            0].lower() else message.text.split()[2:]
        try:
            yaxta = Yaxta(user_id=message.from_user.id)
        except:
            yaxta = None
            if len(arg) < 1 or arg[0].lower() != 'купить':
                return await yaxti_list_handler(message)
            try:
                if not arg[1].isdigit():
                    return await yaxti_list_handler(message)
            except:
                return await yaxti_list_handler(message)
        if len(arg) == 0:
            return await message.reply(text=yaxta.text, reply_markup=yaxta_kb.as_markup())
        elif arg[0].lower() in ['список', 'лист']:
            return await yaxti_list_handler(message)

        elif arg[0].lower() == 'продать':
            doxod = yaxta.sell()
            sql.execute(f'UPDATE users SET bank = bank + {doxod} WHERE id = {message.from_user.id}')
            await message.reply(f'✅ Вы продали яхту и с учётом налогов, и дохода вы получили: {to_str(doxod)}',
                                reply_markup=show_balance_kb.as_markup())

            return
        elif arg[0].lower() == 'купить':
            if yaxta:
                return await message.reply('❗ У вас уже есть яхта, можно иметь только 1.',
                                           reply_markup=show_yaxta_kb.as_markup())
            try:
                i = yaxti[int(arg[1])]
            except:
                return await message.reply('❌ Ошибка. Неверный номер яхты! 1-4')
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
            Yaxta.create(user_id=message.from_user.id, yaxta_index=int(arg[1]))
            sql.execute(f'UPDATE users SET balance = balance - {price}, sell_count = 0 WHERE id ='
                        f' {message.from_user.id}', True)
            await message.reply(f'✅ Вы успешно приобрели яхту <b>{i["name"]}</b> за'
                                f' {to_str(price)}', reply_markup=show_yaxta_kb.as_markup())

            return
        elif arg[0].lower() in ['снять', 'доход']:
            xd = yaxta.cash
            if len(arg) > 1:
                try:
                    xd = get_cash(arg[1])
                except:
                    pass
            if yaxta.cash < xd or yaxta.cash < 0:
                return await message.reply('💲 Недостаточно денег на счету яхты!')
            elif xd <= 0:
                return await message.reply('❌ Нельзя так!')
            sql.executescript(f'''UPDATE users SET bank = bank + {xd} WHERE id = {message.from_user.id};
                                  UPDATE yaxti SET cash = cash - {xd} WHERE owner = {yaxta.owner};''',
                              True)

            await message.reply(f'✅ Вы успешно сняли {to_str(xd)} с прибыли яхты!')

            return
        elif arg[0].lower() in ['плыть']:
            lol = datetime.now() - yaxta.time_buy
            if lol.total_seconds() < 2400:
                xd = f'{round((2400 - lol.total_seconds()) / 60)} мин.'
                return await message.reply(f'🚢️ Яхта новая ее можно использовать через: {xd}')
            if yaxta.fuel <= 0:
                return await message.reply('🚢️ Яхта больше не может ехать! Её состояние: 0%\n'
                                           'Вам нужно <b>Болтик 🔩</b> (x10) чтобы восстановить 1%\n\nВведите <code>'
                                           ' Яхта починить</code> чтобы починить яхту',
                                           reply_markup=show_yaxta_kb.as_markup())
            elif yaxta.energy <= 0:
                return await message.reply('⚡ У яхты разрядился аккумулятор, подождите немного чтобы он зарядился!')

            doxod = yaxta.ride()
            await message.reply(f'🚢️ Вы проехали {doxod[0]} км. и заработали {to_str(doxod[1])}'
                                f' на счёт яхты! (-1⚡) (-1⛽)\n'
                                f'⚡ Текущая энергия: {yaxta.energy}\n'
                                f'⛽ Текущее состояние яхты: {yaxta.fuel}%',
                                reply_markup=ride_yaxta_kb.as_markup())

            return

        elif arg[0].lower() in ['починить', 'чинить', 'починка']:
            items = sql.execute(f'SELECT items FROM users WHERE id = {message.from_user.id}', False, True)[0][0]
            if '22:' not in items:
                return await message.reply('❌ У вас нет <b>Болтик 🔩</b> (x10) в инвентаре!',
                                           reply_markup=show_inv_kb.as_markup())
            count = int(items.split('22:')[1].split(',')[0])
            if count < 10:
                return await message.reply(f'❌ Не хватает {10 - count} <b>Болтиков 🔩</b> для починки!',
                                           reply_markup=show_inv_kb.as_markup())

            user_items = [[int(x.split(':')[0]), int(x.split(':')[1])] for x in items.split(',') if x]
            for index, i in enumerate(user_items):
                if i[0] == 22:
                    break
            user_items[index] = [22, i[1] - 10]
            if (i[1] - 10) <= 0:
                user_items.remove(user_items[index])
            str_items = ','.join(f'{x[0]}:{x[1]}' for x in user_items if x)
            sql.executescript(f"UPDATE users SET items = '{str_items}' WHERE id = {message.from_user.id};\n"
                              f"UPDATE yaxti SET fuel = fuel + 1 WHERE owner = {yaxta.owner};")

            await message.reply('✅ Яхта восстановлен на +1%')

            return

        elif arg[0].lower() in ['оплата', 'оплатить', 'налог', 'налоги']:
            xd = yaxta.nalog
            if len(arg) > 1:
                try:
                    xd = get_cash(arg[1])
                except:
                    pass
            if yaxta.nalog < 1:
                return await message.reply('💲 Налог на яхту и так оплачен!')
            elif yaxta.nalog < xd:
                xd = yaxta.nalog
            elif xd <= 0:
                return await message.reply('❌ Нельзя так!')
            if sql.execute(f'SELECT bank FROM users WHERE id = {message.from_user.id}', False, True)[0][0] < xd:
                return await message.reply(f'💲 Недостаточно денег в банке для оплаты налога, нужно: {to_str(xd)}!',
                                           reply_markup=show_balance_kb.as_markup())

            sql.executescript(f'''UPDATE users SET bank = bank - {xd} WHERE id = {message.from_user.id};
                                  UPDATE yaxti SET nalog = {yaxta.nalog - xd} WHERE owner = {yaxta.owner};''',
                              True)

            await message.reply('✅ Налог на яхту успешно оплачен!')

            return
        else:
            return await message.reply(
                '❌ Ошибка. Используйте: <code>Яхта (снять\оплатить\плыть\починить) (сумма)</code>')
