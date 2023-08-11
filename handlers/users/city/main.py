from datetime import datetime
import re

from aiogram import flags
from aiogram.types import Message

from config import bot_name
from keyboard.generate import show_city_kb, city_water_kb, city_electro_kb, city_road_kb, city_build_kb, city_house_kb
from utils.city.city import City
from utils.main.cash import to_str
from utils.main.db import sql
from filters.users import flood_handler
from utils.main.users import User
from utils.city.buildings import water_build, energy_build, house_build
from utils.quests.main import QuestUser

numbers_emoji = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']


def count_build(counter: list = None):
    count = 0
    for index, builds in enumerate(counter, start=1):
        count += counter[f"{index}"]["count_build"]

    return count


def count_build_get(counter: list = None):
    count = 0
    for index, item in enumerate(counter, start=1):
        build = water_build[index]
        count += counter[f"{index}"]["count_build"] * build['get']
    return count


@flags.throttling_key('default')
async def city_info_handler(message: Message):
    user = User(user=message.from_user)
    text = f'{user.link} ,постройте город и зарабатывайте огромные деньги!\n' \
           '🏙 Город - информация о Вашем городе\n' \
           '⚒ Город основать - построить город\n' \
           '✒️ Город ник [название]\n' \
           '🏘 Город здания - список зданий в городе\n' \
           '🏗 Город построить [воду\электро\дом] - построить здание\n' \
           '🚙 Город дорога [метры] - построить дороги\n' \
           '💸 Город налог [1-99] - изменить налоги\n' \
           '💰 Город казна - казна банка \n'
    return await message.reply(text, disable_web_page_preview=True)


@flags.throttling_key('default')
async def city_handler(message: Message):
    flood = await flood_handler(message)
    if flood:
        arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[
            0].lower() else message.text.split()[2:]
        try:
            city = City(user_id=message.from_user.id)
            city.edit('last_online', datetime.now().strftime('%d-%m-%Y %H:%M:%S'))
        except:
            city = None
            if len(arg) < 1 or arg[0].lower() != 'основать':
                return await city_info_handler(message)
        user = User(user=message.from_user)
        if len(arg) == 0:
            count_house = count_build(city.house)
            count_energy = count_build_get(city.energy)
            count_water = count_build_get(city.water)
            builds = city.get_count_build()
            happynes = city.happynes
            problems = ''
            notification = "➖➖➖➖➖➖➖➖➖➖➖\n⚠️ В городе есть проблемы"
            if count_energy < count_house * 165:
                happynes -= 20
                problems += '⚡️ Расходы электроэнергии превышают её выработки!\n' \
                            '➖ Постройте электростанцию\n'
            if count_water < count_house * 145:
                happynes -= 20
                problems += '💦 Расходы воды превышают её добычу!\n' \
                            '➖ Постройте водонапорную башню\n'
            text = f'<b>{user.link}</b>, информация о Вашем городе:\n\n' \
                   f'➖➖➖➖➖➖➖➖➖➖➖\n' \
                   f'🏙 Название: <b>{city.name}</b>\n\n' \
                   f'💰 Казна города: {to_str(city.kazna)}\n' \
                   f'👥 Жителей: {city.citizens}\n' \
                   f'{"🤬" if happynes < 30 else "🙂"} Счастье: {round(happynes, 2)}%\n' \
                   f'👨🏻‍🔧 Работают: {city.workers}\n' \
                   f'💸 Налоги: {city.taxes}%\n' \
                   f'➖➖➖➖➖➖➖➖➖➖➖\n' \
                   f'💧 Вода: {count_water}/{count_house * 145} м³/сутки\n' \
                   f'⚡ Энергия: {count_energy}/{count_house * 165} МВт\n' \
                   f'🚙 Дороги: {city.road}\n' \
                   f'{problems if problems == "" else notification}\n' \
                   f'{problems}' \
                   f'➖➖➖➖➖➖➖➖➖➖➖\n' \
                   f'🏗 Зданий: {builds}'

            await message.reply(text=text, disable_web_page_preview=True, reply_markup=city_build_kb.as_markup())
            result = QuestUser(user_id=user.id).check_progres(quest_ids=[12, 13, 14, 15],
                                                              progresses=[city.citizens, count_house,
                                                                          count_build(city.energy),
                                                                          count_build(city.water)])
            if result != '':
                await message.answer(text=result.format(user=user.link), disable_web_page_preview=True)
            return
        elif arg[0].lower() in ['инфо']:
            return await city_info_handler(message)

        elif arg[0].lower() == 'основать':
            if city:
                return await message.reply('❗ У вас уже есть город, можно иметь только 1.',
                                           reply_markup=show_city_kb.as_markup())
            try:
                name = arg[1]
                args = re.sub('''[@"'%<>💎👨‍🔬🌟⚡👮‍♂➪👾🥲⛏😎👑💖🐟🍆😈🏿🐥👶🏿🇷🇺🇺🇦]''', '', name)
                if len(args) > 16 or len(args) < 4:
                    return await message.reply('❌ Ошибка! Максимальная длина названия: 16, Минимальная: 6\n'
                                               'Также в названиях разрешены только цифры, англ. и рус. буквы!')
            except:
                return await message.reply('❌ Ошибка. Используйте: <code>город основать (назв)</code>',
                                           reply_markup=show_city_kb.as_markup())
            balance = sql.execute(f'SELECT balance FROM users WHERE id = {message.from_user.id}', False, True)[0][0]

            price = 100000000

            if balance < price:
                return await message.reply(
                    f'💲 На руках недостаточно денег для покупки, нужно: {to_str(price)}')
            City.create(user_id=message.from_user.id, name=args)
            sql.execute(f'UPDATE users SET balance = balance - {price} WHERE id ='
                        f' {message.from_user.id}', True)
            return await message.reply(f'✅ Вы успешно построили город  <b>{args}</b> за'
                                       f' {to_str(price)}', reply_markup=show_city_kb.as_markup())

        elif arg[0].lower() == 'построить':
            if city:

                try:
                    name = arg[1].lower()
                except:
                    return await message.reply('❌ Ошибка. Используйте: <code>город построить (назв)</code>',
                                               reply_markup=show_city_kb.as_markup())
                if name == 'воду':
                    try:
                        item_id = int(arg[2])
                    except:
                        text = f'{user.link}, Доступные вам здания:\n\n'
                        for index, item in enumerate(water_build, start=1):
                            try:
                                build = water_build[index]
                                text += f"{index}. {build['name']}({to_str(build['price'])})\n"
                            except Exception as ex:
                                print(f'{item}: {ex}')
                        return await message.reply(
                            text + "\n❔ Введите «Город построить воду [номер]» для строительства ",
                            reply_markup=city_water_kb.as_markup(), disable_web_page_preview=True)
                    try:
                        item = water_build[item_id]
                    except:
                        return await message.reply('🚫 Неверный номер предмета!')

                    price = (item['price'])
                    builds = city.get_count_build()

                    if builds * 2 > city.road:
                        return await message.reply(f'Вы не можете построить это здание:\n'
                                                   '🚧 В городе нет свободных дорог, рядом с которыми можно построить это здание. ')
                    if user.balance < price:
                        return await message.reply(f'💲 Недостаточно средств на руках, нужно: {to_str(price)}')
                    user.edit('balance', user.balance - price)
                    count = city.water[f'{item_id}']['count_build'] + 1
                    sql.execute(
                        "UPDATE city SET water = jsonb_set(water, "
                        f"'{{{item_id}, count_build}}', "
                        f"'{count}')  WHERE owner={user.id}", commit=True)
                    await message.reply(f'✅ Вы успешно построили «{item["name"]}» '
                                        f'📌 Информация о здании:\n'
                                        f'  💧 Количество зданий: {count} шт.\n'
                                        f'  💧 Добыча воды:{item["get"]} м³/сутки',
                                        reply_markup=city_water_kb.as_markup())
                    result = QuestUser(user_id=user.id).update_progres(quest_ids=15, add_to_progresses=1)
                    if result != '':
                        await message.answer(text=result.format(user=user.link), disable_web_page_preview=True)
                    return

                if name == 'электро':
                    try:
                        item_id = int(arg[2])
                    except:
                        text = f'{user.link}, Доступные вам здания:\n\n'
                        for index, item in enumerate(energy_build, start=1):
                            try:
                                build = energy_build[index]
                                text += f"{index}. {build['name']}({to_str(build['price'])})\n"
                            except Exception as ex:
                                print(f'{item}: {ex}')
                        return await message.reply(
                            text + "\n❔ Введите «Город построить электро [номер]» для строительства ",
                            reply_markup=city_electro_kb.as_markup(), disable_web_page_preview=True)
                    try:
                        item = energy_build[item_id]
                    except:
                        return await message.reply('🚫 Неверный номер предмета!')

                    price = (item['price'])

                    if user.balance < price:
                        return await message.reply(f'💲 Недостаточно средств на руках, нужно: {to_str(price)}')
                    builds = city.get_count_build()

                    if builds * 2 > city.road:
                        return await message.reply(f'Вы не можете построить это здание:\n'
                                                   '🚧 В городе нет свободных дорог, рядом с которыми можно построить это здание. ')
                    user.edit('balance', user.balance - price)
                    count = city.energy[f'{item_id}']['count_build'] + 1

                    sql.execute(
                        "UPDATE city SET energy = jsonb_set(energy, "
                        f"'{{{item_id}, count_build}}', "
                        f"'{count}') WHERE owner={user.id}", commit=True)
                    await message.reply(f'✅ Вы успешно построили  «{item["name"]}»'
                                        f'📌 Информация о здании:\n'
                                        f' ⚡ Количество зданий: {count} шт.\n'
                                        f'  Выработка энергии: {item["get"]} КВт',
                                        reply_markup=city_electro_kb.as_markup())
                    result = QuestUser(user_id=user.id).update_progres(quest_ids=14, add_to_progresses=1)
                    if result != '':
                        await message.answer(text=result.format(user=user.link), disable_web_page_preview=True)
                    return
                if name == 'дом':
                    try:
                        item_id = int(arg[2])
                    except:
                        text = f'{user.link}, Доступные вам здания:\n\n'
                        for index, item in enumerate(house_build, start=1):
                            try:
                                build = house_build[index]
                                text += f"{index}. {build['name']}({to_str(build['price'])})\n"
                            except Exception as ex:
                                print(f'{item}: {ex}')
                        return await message.reply(
                            text + "\n❔ Введите «Город построить дом [номер]» для строительства ",
                            reply_markup=city_house_kb.as_markup(), disable_web_page_preview=True)
                    try:
                        item = house_build[item_id]
                    except:
                        return await message.reply('🚫 Неверный номер предмета!')

                    price = (item['price'])

                    if user.balance < price:
                        return await message.reply(f'💲 Недостаточно средств на руках, нужно: {to_str(price)}')

                    builds = city.get_count_build()
                    if builds * 2 > city.road:
                        return await message.reply(f'Вы не можете построить это здание:\n'
                                                   '🚧 В городе нет свободных дорог, рядом с которыми можно построить это здание. ')
                    user.edit('balance', user.balance - price)
                    count = city.house[f'{item_id}']['count_build'] + 1

                    sql.execute(
                        "UPDATE city SET house = jsonb_set(house, "
                        f"'{{{item_id}, count_build}}', "
                        f"'{count}') WHERE owner={user.id}", commit=True)
                    await message.reply(f'✅ Вы успешно построили  «{item["name"]}»'
                                        f'📌 Информация о здании:\n'
                                        f' 👤 Количество зданий: {count} шт.\n'
                                        f' 👤 Вместимость жителей: {item["capacity"]} ',
                                        reply_markup=city_house_kb.as_markup())
                    result = QuestUser(user_id=user.id).update_progres(quest_ids=13, add_to_progresses=1)
                    if result != '':
                        await message.answer(text=result.format(user=user.link), disable_web_page_preview=True)
                    return

            else:
                return await message.reply('❌ Ошибка. Используйте: <code>город построить (назв)</code>',
                                           reply_markup=show_city_kb.as_markup())
        elif arg[0].lower() == 'дорога':
            try:
                count = abs(int(arg[1]))

            except:
                return await message.reply('🚫 Используйте: <code>город дорога {кол-во}</code>')

            price = 20000 * count

            if user.balance < price:
                return await message.reply(f'💲 Недостаточно средств на руках, нужно: {to_str(price)}')
            user.edit('balance', user.balance - price)
            city.edit('road', city.road + count)
            return await message.reply(f'✅ Вы успешно проложили  «{count}» метров.',
                                       reply_markup=city_road_kb.as_markup())
        elif arg[0].lower() == 'налог':
            try:
                count = int(arg[1])
                if count > 99 or count < 1:
                    return await message.reply('🚫 Используйте: <code>город налог [1-99]</code>')
            except:
                return await message.reply('🚫 Используйте: <code>город налог [1-99]</code>')

            city.edit('taxes', count)
            return await message.reply(f'✅ Вы успешно изменили размер налоговой ставки  «{count}».',
                                       reply_markup=show_city_kb.as_markup())
        elif arg[0].lower() == 'казна':
            if city.kazna <= 0:
                return await message.reply(f'🚫 На балансе казны 0$', reply_markup=show_city_kb.as_markup())
            await message.reply(f'✅ Вы успешно сняли с казны  «{to_str(city.kazna)}».',
                                reply_markup=show_city_kb.as_markup())
            user.edit('balance', user.balance + city.kazna)
            city.edit('kazna', 0)
            result = QuestUser(user_id=user.id).update_progres(quest_ids=19, add_to_progresses=1)
            if result != '':
                await message.answer(text=result.format(user=user.link), disable_web_page_preview=True)
            return

        elif arg[0].lower() == 'здания':
            text = '🏡 Все здания в городе:\n'
            count = 1
            for index, builds in enumerate(city.water, start=1):
                emoji = ''.join(numbers_emoji[int(i)] for i in str(count))
                build = water_build[index]
                text += f'{emoji}. {build["name"]} - ({city.water[f"{index}"]["count_build"]}) \n'
                count += 1
            for index, builds in enumerate(city.energy, start=1):
                emoji = ''.join(numbers_emoji[int(i)] for i in str(count))
                build = energy_build[index]
                text += f'{emoji}. {build["name"]} - ({city.energy[f"{index}"]["count_build"]}) \n'
                count += 1
            for index, builds in enumerate(city.house, start=1):
                emoji = ''.join(numbers_emoji[int(i)] for i in str(count))
                build = house_build[index]
                text += f'{emoji}. {build["name"]} - ({city.house[f"{index}"]["count_build"]}) \n'
                count += 1
            return await message.reply(text=text, disable_web_page_preview=True)

        elif arg[0].lower() == 'ник':
            args = re.sub('''[@"'%<>💎👨‍🔬🌟⚡👮‍♂➪👾🥲⛏😎👑💖🐟🍆😈🏿🐥👶🏿🇷🇺🇺🇦]''', '', arg[1])
            if not args:
                return await message.reply(f'👓 Никнейм города: <b>{city.name}</b>')
            else:
                if len(args) > 16 or len(args) < 4:
                    return await message.reply('❌ Ошибка! Максимальная длина ника: 16, Минимальная: 6\n'
                                               'Также в никах разрешены только цифры, англ. и рус. буквы!')
                city.edit('name', args)
                await message.reply(f'✅ Названия города успешно изменён на: <code>{city.name}</code>',
                                    reply_markup=show_city_kb.as_markup())

        else:
            return await message.reply('❌ Ошибка. Используйте: <code>Город</code>')
