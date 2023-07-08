from datetime import datetime

from aiogram import flags
from aiogram.types import Message

from config import bot_name
from keyboard.generate import show_balance_kb, show_inv_kb, show_moto_kb, moto_kb, buy_moto_kb, ride_moto_kb

from utils.main.moto import motos, Moto
from utils.main.cash import to_str, get_cash
from utils.main.db import sql
from filters.users import flood_handler

numbers_emoji = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']


@flags.throttling_key('default')
async def moto_list_handler(message: Message):
    text = '🏍️ Список мотоциклов:\n'

    for index, i in motos.items():
        emoji = ''.join(numbers_emoji[int(i)] for i in str(index))

        text += f'<code>{emoji}</code>.{i["name"]}\n' \
                f'💵 Цена: {to_str(i["price"])} \n' \
                f'💲 Налог: {to_str(i["nalog"])}\n\n'
    return await message.reply(text + '\nИспользуйте: <code>мотоцикл купить (номер)</code> чтобы купить!',
                               reply_markup=buy_moto_kb.as_markup())


@flags.throttling_key('default')
async def moto_handler(message: Message):
    flood = await flood_handler(message)
    if flood:
        arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[
            0].lower() else message.text.split()[2:]
        try:
            moto = Moto(user_id=message.from_user.id)
        except:
            moto = None
            if len(arg) < 1 or arg[0].lower() != 'купить':
                return await moto_list_handler(message)
            try:
                if not arg[1].isdigit():
                    return await moto_list_handler(message)
            except:
                return await moto_list_handler(message)
        if len(arg) == 0:
            return await message.reply(text=moto.text, reply_markup=moto_kb.as_markup())
        elif arg[0].lower() in ['список', 'лист']:
            return await moto_list_handler(message)

        elif arg[0].lower() == 'продать':
            doxod = moto.sell()
            sql.execute(f'UPDATE users SET bank = bank + {doxod} WHERE id = {message.from_user.id}')
            await message.reply(f'✅ Вы продали мотоцикл и с учётом налогов, и дохода вы получили: {to_str(doxod)}',
                                reply_markup=show_balance_kb.as_markup())

            return
        elif arg[0].lower() == 'купить':
            if moto:
                return await message.reply('❗ У вас уже есть мотоцикл, можно иметь только 1.',
                                           reply_markup=show_moto_kb.as_markup())
            try:
                i = motos[int(arg[1])]
            except:
                return await message.reply('❌ Ошибка. Неверный номер мотоцикла! 1-6')
            balance = \
                sql.execute(f'SELECT balance FROM users WHERE id = {message.from_user.id}', commit=False,
                            fetchone=True)[0]
            price = i["price"]

            if balance < price:
                return await message.reply(
                    f'💲 На руках недостаточно денег для покупки, нужно: {to_str(price)}')
            Moto.create(user_id=message.from_user.id, moto_index=int(arg[1]))
            sql.execute(f'UPDATE users SET balance = balance - {price}, sell_count = 0 WHERE id ='
                        f' {message.from_user.id}', True)
            return await message.reply(f'✅ Вы успешно приобрели мотоциклову <b>{i["name"]}</b> за'
                                       f' {to_str(price)}',
                                       reply_markup=show_moto_kb.as_markup())
        elif arg[0].lower() in ['снять', 'доход']:
            xd = moto.cash
            if len(arg) > 1:
                try:
                    xd = get_cash(arg[1])
                except:
                    pass
            if moto.cash < xd or moto.cash < 0:
                return await message.reply('💲 Недостаточно денег на счету мотоцикла!')
            elif xd <= 0:
                return await message.reply('❌ Нельзя так!')
            sql.executescript(f'''UPDATE users SET bank = bank + {xd} WHERE id = {message.from_user.id};
                                  UPDATE moto SET cash = cash - {xd} WHERE owner = {moto.owner};''',
                              True)

            await message.reply(f'✅ Вы успешно сняли {to_str(xd)} с прибыли мотоцикла!')
        elif arg[0].lower() in ['ехать']:
            lol = datetime.now() - moto.time_buy
            if lol.total_seconds() < 2400:
                xd = f'{round((2400 - lol.total_seconds()) / 60)} мин.'
                return await message.reply(f'🏍️ мотоцикл новый его можно использовать через: {xd}')
            if moto.fuel <= 0:
                return await message.reply('🏍️ мотоцикл больше не может ехать! Её состояние: 0%\n'
                                           'Вам нужно <b>Болтик 🔩</b> (x10) чтобы восстановить 1%\n\nВведите <code>'
                                           ' мотоцикл починить</code> чтобы починить мотоциклову',
                                           reply_markup=show_moto_kb.as_markup())
            elif moto.energy <= 0:
                return await message.reply(
                    '⚡ У мотоцикла разрядился аккумулятор, подождите немного чтобы он зарядился!')

            doxod = moto.ride()
            return await message.reply(f'🏍️ Вы проехали {doxod[0]} км. и заработали {to_str(doxod[1])}'
                                       f' на счёт мотоцикла! (-1⚡) (-1⛽)\n'
                                       f'⚡ Текущая энергия: {moto.energy}\n'
                                       f'⛽ Текущее состояние мотоцикла: {moto.fuel}%',
                                       reply_markup=ride_moto_kb.as_markup())

        elif arg[0].lower() in ['починить', 'чинить', 'починка']:
            items = sql.execute(f'SELECT items FROM users WHERE id = {message.from_user.id}', False, True)[0][0]

            if items['8']['count'] < 10:
                return await message.reply(
                    f"❌ Не хватает {10 - items['8']['count']} <b>Болтиков 🔩</b> для починки!'",
                    reply_markup=show_inv_kb.as_markup())

            count_items = items['8']['count'] - 10
            sql.executescript(f"UPDATE users SET items = jsonb_set(items, "
                              "'{8, count}', "
                              f"'{count_items}') WHERE id={message.from_user.id};\n"
                              f"UPDATE moto SET fuel = fuel + 1 WHERE owner = {moto.owner};")

            return await message.reply('✅ мотоцикл восстановлен на +1%')

        elif arg[0].lower() in ['оплата', 'оплатить', 'налог', 'налоги']:
            xd = moto.nalog
            if len(arg) > 1:
                try:
                    xd = get_cash(arg[1])
                except:
                    pass
            if moto.nalog < 1:
                return await message.reply('💲 Налог на мотоцикл и так оплачен!')
            elif moto.nalog < xd:
                xd = moto.nalog
            elif xd <= 0:
                return await message.reply('❌ Нельзя так!')
            if sql.execute(f'SELECT bank FROM users WHERE id = {message.from_user.id}', False, True)[0][0] < xd:
                return await message.reply(f'💲 Недостаточно денег в банке для оплаты налога, нужно: {to_str(xd)}!',
                                           reply_markup=show_balance_kb.as_markup())

            sql.executescript(f'''UPDATE users SET bank = bank - {xd} WHERE id = {message.from_user.id};
                                  UPDATE moto SET nalog = {moto.nalog - xd} WHERE owner = {moto.owner};''',
                              True)

            return await message.reply('✅ Налог на мотоцикл успешно оплачен!')
        else:
            return await message.reply('❌ Ошибка. Используйте: <code>мотоцикл (снять\оплатить\ехать) (сумма)</code>')
