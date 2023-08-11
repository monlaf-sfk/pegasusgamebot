from datetime import datetime

from aiogram import flags
from aiogram.types import Message

from config import bot_name
from keyboard.generate import buy_airplane_kb, show_balance_kb, show_inv_kb, show_airplane_kb, airplane_kb, \
    ride_airplane_kb
from utils.items.work_items import set_workitems_count, get_workitems_count

from utils.main.airplanes import airplanes, Airplane
from utils.main.cash import to_str, get_cash
from utils.main.db import sql
from filters.users import flood_handler

numbers_emoji = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']


@flags.throttling_key('default')
async def airplanes_list_handler(message: Message):
    text = '✈️Список самолетов:\n'

    for index, i in airplanes.items():
        emoji = ''.join(numbers_emoji[int(i)] for i in str(index))

        text += f'<code>{emoji}</code>.{i["name"]}\n' \
                f'💵 Цена: {to_str(i["price"])} \n' \
                f'💲 Налог: {to_str(i["nalog"])}\n\n'
    return await message.reply(text + '\nИспользуйте: <code>Самолёт купить (номер)</code> чтобы купить!',
                               reply_markup=buy_airplane_kb.as_markup())


@flags.throttling_key('default')
async def airplanes_handler(message: Message):
    flood = await flood_handler(message)
    if flood:
        arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[
            0].lower() else message.text.split()[2:]
        try:
            airplane = Airplane(user_id=message.from_user.id)
        except:
            airplane = None
            if len(arg) < 1 or arg[0].lower() != 'купить':
                return await airplanes_list_handler(message)
            try:
                if not arg[1].isdigit():
                    return await airplanes_list_handler(message)
            except:
                return await airplanes_list_handler(message)
        if len(arg) == 0:
            return await message.reply(text=airplane.text, reply_markup=airplane_kb.as_markup())
        elif arg[0].lower() in ['список', 'лист']:
            return await airplanes_list_handler(message)

        elif arg[0].lower() == 'продать':
            doxod = airplane.sell()
            sql.execute(f'UPDATE users SET bank = bank + {doxod} WHERE id = {message.from_user.id}')
            await message.reply(f'✅ Вы продали самолёт и с учётом налогов, и дохода вы получили: {to_str(doxod)}',
                                reply_markup=show_balance_kb.as_markup())

            return
        elif arg[0].lower() == 'купить':
            if airplane:
                return await message.reply('❗ У вас уже есть самолёт, можно иметь только 1.',
                                           reply_markup=show_airplane_kb.as_markup())
            try:
                i = airplanes[int(arg[1])]
            except:
                return await message.reply('❌ Ошибка. Неверный номер самолёты! 1-4')
            balance = \
                sql.execute(f'SELECT balance FROM users WHERE id = {message.from_user.id}', commit=False,
                            fetchone=True)[0]
            price = i["price"]

            if balance < price:
                return await message.reply(
                    f'💲 На руках недостаточно денег для покупки, нужно: {to_str(price)}')
            Airplane.create(user_id=message.from_user.id, airplane_index=int(arg[1]))
            sql.execute(f'UPDATE users SET balance = balance - {price} WHERE id ='
                        f' {message.from_user.id}', True)
            await message.reply(f'✅ Вы успешно приобрели самолёт <b>{i["name"]}</b> за'
                                f' {to_str(price)}', reply_markup=show_airplane_kb.as_markup())

            return
        elif arg[0].lower() in ['снять', 'доход']:
            xd = airplane.cash
            if len(arg) > 1:
                try:
                    xd = get_cash(arg[1])
                except:
                    pass
            if airplane.cash < xd or airplane.cash < 0:
                return await message.reply('💲 Недостаточно денег на счету самолёты!')
            elif xd <= 0:
                return await message.reply('❌ Нельзя так!')
            sql.executescript(f'''UPDATE users SET bank = bank + {xd} WHERE id = {message.from_user.id};
                                  UPDATE airplanes SET cash = cash - {xd} WHERE owner = {message.from_user.id};''',
                              True)

            await message.reply(f'✅ Вы успешно сняли {to_str(xd)} с прибыли самолёта!',
                                reply_markup=show_balance_kb.as_markup())

            return
        elif arg[0].lower() in ['лететь', 'летать']:
            lol = datetime.now() - airplane.time_buy
            if lol.total_seconds() < 2400:
                xd = f'{round((2400 - lol.total_seconds()) / 60)} мин.'
                return await message.reply(f'✈️ Самолёт новый его можно использовать через: {xd}')
            if airplane.fuel <= 0:
                return await message.reply('✈️ Самолёт больше не может летать! Его состояние: 0%\n'
                                           'Вам нужно <b>Болтик 🔩</b> (x10) чтобы восстановить 1%\n\nВведите <code>'
                                           ' Самолёт починить</code> чтобы починить самолёт',
                                           reply_markup=show_airplane_kb.as_markup())
            elif airplane.energy <= 0:
                return await message.reply('⚡ У самолёты разрядился аккумулятор, подождите немного чтобы он зарядился!')

            doxod = airplane.ride()
            await message.reply(f'✈️️ Вы проехали {doxod[0]} км. и заработали {to_str(doxod[1])}'
                                f' на счёт самолёты! (-1⚡) (-1⛽)\n'
                                f'⚡ Текущая энергия: {airplane.energy}\n'
                                f'⛽ Текущее состояние самолёты: {airplane.fuel}%',
                                reply_markup=ride_airplane_kb.as_markup())

            return

        elif arg[0].lower() in ['починить', 'чинить', 'починка']:
            count_user = get_workitems_count(8, message.from_user.id)

            if not count_user or count_user < 10:
                count_user = 0 if not count_user else count_user
                return await message.reply(
                    f"❌ Не хватает {10 - count_user} <b>Болтиков 🔩</b> для починки!'",
                    reply_markup=show_inv_kb.as_markup())

            set_workitems_count(8, message.from_user.id, count_user - 10)

            sql.executescript(f'UPDATE airplanes SET fuel = fuel + 1 WHERE owner = {message.from_user.id};')
            await message.reply('✅ Самолёт восстановлен на +1%')

            return

        elif arg[0].lower() in ['оплата', 'оплатить', 'налог', 'налоги']:
            xd = airplane.nalog
            if len(arg) > 1:
                try:
                    xd = get_cash(arg[1])
                except:
                    pass
            if airplane.nalog < 1:
                return await message.reply('💲 Налог на самолёт и так оплачен!')
            elif airplane.nalog < xd:
                xd = airplane.nalog
            elif xd <= 0:
                return await message.reply('❌ Нельзя так!')
            if sql.execute(f'SELECT bank FROM users WHERE id = {message.from_user.id}', False, True)[0][0] < xd:
                return await message.reply(f'💲 Недостаточно денег в банке для оплаты налога, нужно: {to_str(xd)}!',
                                           reply_markup=show_balance_kb.as_markup())

            sql.executescript(f'''UPDATE users SET bank = bank - {xd} WHERE id = {message.from_user.id};
                                  UPDATE airplanes SET nalog = {airplane.nalog - xd} WHERE owner = {message.from_user.id};''',
                              True)

            await message.reply('✅ Налог на самолёт успешно оплачен!')

            return
        else:
            return await message.reply('❌ Ошибка. Используйте: <code>Самолёт (снять\оплатить\ехать) (сумма)</code>')
