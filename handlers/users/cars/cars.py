from datetime import datetime

from aiogram import flags
from aiogram.types import Message

from config import bot_name
from keyboard.generate import show_balance_kb, show_inv_kb, show_car_kb, car_kb, buy_car_kb, ride_car_kb
from utils.items.work_items import set_workitems_count, get_workitems_count

from utils.main.cars import cars, Car
from utils.main.cash import to_str, get_cash
from utils.main.db import sql
from filters.users import flood_handler

numbers_emoji = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']


@flags.throttling_key('default')
async def cars_list_handler(message: Message):
    text = '🚗️ Список машин:\n'

    for index, i in cars.items():
        emoji = ''.join(numbers_emoji[int(i)] for i in str(index))

        text += f'<code>{emoji}</code>.{i["name"]}\n' \
                f'💵 Цена: {to_str(i["price"])} \n' \
                f'💲 Налог: {to_str(i["nalog"])}\n\n'
    return await message.reply(text + '\nИспользуйте: <code>Машина купить (номер)</code> чтобы купить!',
                               reply_markup=buy_car_kb.as_markup())


@flags.throttling_key('default')
async def cars_handler(message: Message):
    flood = await flood_handler(message)
    if flood:
        arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[
            0].lower() else message.text.split()[2:]
        try:
            car = Car(user_id=message.from_user.id)
        except:
            car = None
            if len(arg) < 1 or arg[0].lower() != 'купить':
                return await cars_list_handler(message)
            try:
                if not arg[1].isdigit():
                    return await cars_list_handler(message)
            except:
                return await cars_list_handler(message)
        if len(arg) == 0:
            return await message.reply(text=car.text, reply_markup=car_kb.as_markup())
        elif arg[0].lower() in ['список', 'лист']:
            return await cars_list_handler(message)

        elif arg[0].lower() == 'продать':
            doxod = car.sell()
            sql.execute(f'UPDATE users SET bank = bank + {doxod} WHERE id = {message.from_user.id}')
            await message.reply(f'✅ Вы продали машину и с учётом налогов, и дохода вы получили: {to_str(doxod)}',
                                reply_markup=show_balance_kb.as_markup())

            return
        elif arg[0].lower() == 'купить':
            if car:
                return await message.reply('❗ У вас уже есть машина, можно иметь только 1.',
                                           reply_markup=show_car_kb.as_markup())
            try:
                i = cars[int(arg[1])]
            except:
                return await message.reply('❌ Ошибка. Неверный номер машины!')
            balance = \
                sql.execute(f'SELECT balance FROM users WHERE id = {message.from_user.id}', commit=False,
                            fetchone=True)[0]
            price = i["price"]

            if balance < price:
                return await message.reply(
                    f'💲 На руках недостаточно денег для покупки, нужно: {to_str(price)}')
            Car.create(user_id=message.from_user.id, car_index=int(arg[1]))
            sql.execute(f'UPDATE users SET balance = balance - {price}, sell_count = 0 WHERE id ='
                        f' {message.from_user.id}', True)
            return await message.reply(f'✅ Вы успешно приобрели машину <b>{i["name"]}</b> за'
                                       f' {to_str(price)}', reply_markup=show_car_kb.as_markup())
        elif arg[0].lower() in ['снять', 'доход']:
            xd = car.cash
            if len(arg) > 1:
                try:
                    xd = get_cash(arg[1])
                except:
                    pass
            if car.cash < xd or car.cash < 0:
                return await message.reply('💲 Недостаточно денег на счету машины!',
                                           reply_markup=show_car_kb.as_markup())
            elif xd <= 0:
                return await message.reply('❌ Нельзя так!')
            sql.executescript(f'''UPDATE users SET bank = bank + {xd} WHERE id = {message.from_user.id};
                                  UPDATE cars SET cash = cash - {xd} WHERE owner = {car.owner};''',
                              True)

            await message.reply(f'✅ Вы успешно сняли {to_str(xd)} с прибыли машины!',
                                reply_markup=show_balance_kb.as_markup())
        elif arg[0].lower() in ['ехать']:
            lol = datetime.now() - car.time_buy
            if lol.total_seconds() < 2400:
                xd = f'{round((2400 - lol.total_seconds()) / 60)} мин.'
                return await message.reply(f'🏎️ Машина новая ее можно использовать через: {xd}')
            if car.fuel <= 0:
                return await message.reply('🏎️ Машина больше не может ехать! Её состояние: 0%\n'
                                           'Вам нужно <b>Болтик 🔩</b> (x10) чтобы восстановить 1%\n\nВведите <code>'
                                           ' Машина починить</code> чтобы починить машину',
                                           reply_markup=show_car_kb.as_markup())
            elif car.energy <= 0:
                return await message.reply('⚡ У машины разрядился аккумулятор, подождите немного чтобы он зарядился!')

            doxod = car.ride()
            return await message.reply(f'🏎️ Вы проехали {doxod[0]} км. и заработали {to_str(doxod[1])}'
                                       f' на счёт машины! (-1⚡) (-1⛽)\n'
                                       f'⚡ Текущая энергия: {car.energy}\n'
                                       f'⛽ Текущее состояние машины: {car.fuel}%', reply_markup=ride_car_kb.as_markup())

        elif arg[0].lower() in ['починить', 'чинить', 'починка']:
            count_user = get_workitems_count(8, message.from_user.id)

            if not count_user or count_user < 10:
                count_user = 0 if not count_user else count_user
                return await message.reply(
                    f"❌ Не хватает {10 - count_user} <b>Болтиков 🔩</b> для починки!'",
                    reply_markup=show_inv_kb.as_markup())

            set_workitems_count(8, message.from_user.id, count_user - 10)

            sql.executescript(f"UPDATE cars SET fuel = fuel + 1 WHERE owner = {car.owner};")

            return await message.reply('✅ Машина восстановлен на +1%')

        elif arg[0].lower() in ['оплата', 'оплатить', 'налог', 'налоги']:
            xd = car.nalog
            if len(arg) > 1:
                try:
                    xd = get_cash(arg[1])
                except:
                    pass
            if car.nalog < 1:
                return await message.reply('💲 Налог на машину и так оплачен!')
            elif car.nalog < xd:
                xd = car.nalog
            elif xd <= 0:
                return await message.reply('❌ Нельзя так!')
            if sql.execute(f'SELECT bank FROM users WHERE id = {message.from_user.id}', False, True)[0][0] < xd:
                return await message.reply(f'💲 Недостаточно денег в банке для оплаты налога, нужно: {to_str(xd)}!',
                                           reply_markup=show_balance_kb.as_markup())

            sql.executescript(f'''UPDATE users SET bank = bank - {xd} WHERE id = {message.from_user.id};
                                  UPDATE cars SET nalog = {car.nalog - xd} WHERE owner = {car.owner};''',
                              True)

            return await message.reply('✅ Налог на машину успешно оплачен!')
        else:
            return await message.reply('❌ Ошибка. Используйте: <code>Машина (снять\оплатить\ехать) (сумма)</code>')
