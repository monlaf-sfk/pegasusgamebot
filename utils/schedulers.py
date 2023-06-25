import time
from contextlib import suppress
from datetime import datetime, timedelta

from aiogram.exceptions import TelegramBadRequest

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from psycopg2 import Error, OperationalError

import config
from config import donates, set_bitcoin_price, bitcoin_price, uah_price, set_uah_price, set_euro_price, euro_price

from loader import bot
from utils.bosses import bosses

from utils.items.items import item_case
from utils.jobs.jobs import jobs, levels

from utils.main.cars import cars
from utils.main.cash import to_str
from utils.main.db import sql

from threading import Lock

from utils.main.users import User
from utils.promo.promo import Promocode, all_promo
from utils.main.moto import motos
import random
import string

from utils.weapons.swords import ArmoryInv

lock = Lock()


async def limit_check():
    try:
        with lock:
            cursor = sql.conn.cursor()
            query = ''
            data = sql.execute('SELECT id, donate_source FROM users WHERE last_vidacha'
                               f" IS NOT NULL AND TIMESTAMP without time zone '{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}' -  last_vidacha >= '{timedelta(minutes=1439)}'",
                               False, True)
        if data != None:
            for i in data:
                if i[1] != None:
                    x = i[1].split(',')
                    item = donates[int(x[0])]
                    query += f"UPDATE users SET limitvidach={item['limitvidach']},last_vidacha='{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}' WHERE id = {i[0]};\n"
            if query != '':
                with lock:
                    sql.executescript(cursor=cursor,
                                      commit=True,
                                      query=query)
    except (Exception, Error, OperationalError) as ex:
        print('limit_check:', ex)


async def deposit_check():
    try:
        with lock:
            cursor = sql.conn.cursor()

            query = ''

            data = sql.execute('SELECT id, donate_source, deposit FROM users WHERE donate_source'
                               f' IS NOT NULL AND ({time.time()} - deposit_date) >= 43200',
                               False, True)
        for i in data:
            x = i[1].split(',')
            date = datetime.strptime(x[1], '%d-%m-%Y %H:%M')
            if (datetime.now() - date).total_seconds() > 1:
                item = donates[int(x[0])]
                query += f'UPDATE users SET deposit = deposit + cast(ROUND' \
                         f'(deposit * (percent + {item["percent"]})/100) as integer),' \
                         f' deposit_date = {time.time()} WHERE id = {i[0]};\n'
        if query != '':
            with lock:
                sql.executescript(cursor=cursor,
                                  commit=True,
                                  query=query)
        query = f'UPDATE users SET deposit_date = {time.time()}, deposit = deposit +' \
                'cast(ROUND(deposit * (1)/' \
                '100) as integer)' \
                f' WHERE deposit_date IS NOT ' \
                f'NULL AND ' \
                f'({time.time()} - deposit_date) >= 43200 ;\n'

        with lock:
            sql.executescript(cursor=cursor,
                              commit=True,
                              query=query)
        query = f'UPDATE users SET credit_time = {time.time()}, bank = bank - cast(ROUND(credit / 10, ' \
                f'0) as int) ' \
                f'WHERE credit_time IS NOT NULL AND ({time.time()} - credit_time) >= 7200;\n'

        query += f'UPDATE users SET energy = energy + 1, energy_time = {time.time()}' \
                 f' WHERE energy < 20 AND energy_time IS NOT NULL AND (' \
                 f'{time.time()} - energy_time) >= 600;'

        with lock:
            sql.executescript(query, commit=True, cursor=cursor)
        return True
    except Exception as ex:
        print('deposit_check:', ex)


async def check_jobs():
    try:
        with lock:
            cursor = sql.conn.cursor()

            query = 'SELECT id, job_index, level FROM users WHERE work_time' \
                    f' IS NOT NULL AND (job_index > 0 OR (level > 6 AND level < 12)) AND ({time.time()} - ' \
                    f'work_time) >= 3600'
            users = sql.execute(query,
                                False, True, cursor)

        query = f'UPDATE users SET job_time = {time.time()}, level = level + 1 WHERE ({time.time()} - job_time) >= ' \
                f'43200;\n'

        for user in users:
            uid, index, level = user
            job = jobs[index] if index > 0 else levels[level]
            query += f'UPDATE users SET work_time = {time.time()}, bank = bank + {job["doxod"]} WHERE id = {uid};\n'

        with lock:
            sql.executescript(cursor=cursor,
                              query=query,
                              commit=True,
                              fetch=False)
    except Exception as ex:
        print('check_jobs:', ex)


async def cars_check():
    try:

        cursor = sql.conn.cursor()

        query2 = f'SELECT  "index", nalog, owner FROM cars WHERE last is NOT NULL AND ' \
                 f'({time.time()} - last) >= ' \
                 f'3600 AND energy < 10'
        with lock:
            result = sql.execute(query2, False, True, cursor=cursor)

        query3 = ''

        for car_s in result:
            index, nalog, owner = car_s
            car = cars[index]
            if nalog + car["nalog"] > car['limit']:
                pass
            else:
                query3 += f'UPDATE cars SET nalog = nalog + {car["nalog"]}, ' \
                          f'last = {time.time()}, energy = energy + 1 WHERE owner = {owner};\n'
        if query3 != '':
            with lock:
                sql.executescript(query3, True, False, cursor=cursor)
    except Exception as ex:
        print('cars_check:', ex)


async def houses_check():
    try:
        cursor = sql.conn.cursor()
        with lock:
            query3 = f'UPDATE houses SET nalog = nalog + stock_nalog, ' \
                     f'last = {time.time()}, cash = ROUND(cash + stock_doxod) WHERE last is NOT NULL AND ({time.time()} - last) >= 3600 AND stock_nalog*11 >= nalog'
            sql.executescript(query3, True, False, cursor=cursor)
    except Exception as ex:
        print('businesses_check:', ex)


async def businesses_check():
    try:
        cursor = sql.conn.cursor()
        with lock:
            query3 = f'UPDATE businesses SET nalog = nalog + stock_nalog, ' \
                     f'last = {time.time()}, cash = ROUND(cash + stock_doxod) WHERE last is NOT NULL AND ({time.time()} - last) >= 3600 AND stock_nalog*11 >= nalog'
            sql.executescript(query3, True, False, cursor=cursor)
    except Exception as ex:
        print('businesses_check:', ex)


async def yaxti_check():
    try:
        cursor = sql.conn.cursor()

        query2 = f'SELECT "index", nalog, owner FROM yaxti WHERE last is NOT NULL AND ' \
                 f'({time.time()} - last) >= ' \
                 f'3600 AND energy < 10'
        with lock:
            result = sql.execute(query2, False, True, cursor=cursor)

        query3 = ''

        for car_s in result:
            index, nalog, owner = car_s
            car = cars[index]
            if nalog + car["nalog"] > car['limit']:
                pass
            else:
                query3 += f'UPDATE yaxti SET nalog = nalog + {car["nalog"]}, ' \
                          f'last = {time.time()}, energy = energy + 1 WHERE owner = {owner};\n'
        if query3 != '':
            with lock:
                sql.executescript(query3, True, False, cursor=cursor)
    except Exception as ex:
        print('yaxti_check:', ex)


async def vertoleti_check():
    try:
        cursor = sql.conn.cursor()

        query2 = f'SELECT "index", nalog, owner FROM vertoleti WHERE last is NOT NULL AND ' \
                 f'({time.time()} - last) >= ' \
                 f'3600 AND energy < 10'
        with lock:
            result = sql.execute(query2, False, True, cursor=cursor)

        query3 = ''

        for car_s in result:
            index, nalog, owner = car_s
            car = cars[index]
            if nalog + car["nalog"] > car['limit']:
                pass
            else:
                query3 += f'UPDATE vertoleti SET nalog = nalog + {car["nalog"]}, ' \
                          f'last = {time.time()}, energy = energy + 1 WHERE owner = {owner};\n'
        if query3 != '':
            with lock:
                sql.executescript(query3, True, False, cursor=cursor)
    except Exception as ex:
        print('vertoleti_check:', ex)


async def airplanes_check():
    try:
        cursor = sql.conn.cursor()

        query2 = f'SELECT  "index", nalog, owner FROM airplanes WHERE last is NOT NULL AND ' \
                 f'({time.time()} - last) >= ' \
                 f'3600 AND energy < 10'
        with lock:
            result = sql.execute(query2, False, True, cursor=cursor)

        query3 = ''

        for car_s in result:
            index, nalog, owner = car_s
            car = cars[index]
            if nalog + car["nalog"] > car['limit']:
                pass
            else:
                query3 += f'UPDATE airplanes SET nalog = nalog + {car["nalog"]}, ' \
                          f'last = {time.time()}, energy = energy + 1 WHERE owner = {owner};\n'
        if query3 != '':
            with lock:
                sql.executescript(query3, True, False, cursor=cursor)
    except Exception as ex:
        print('airplanes_check:', ex)


async def moto_check():
    try:
        cursor = sql.conn.cursor()

        query2 = f'SELECT "index", nalog, owner FROM moto WHERE last is NOT NULL AND ' \
                 f'({time.time()} - last) >= ' \
                 f'3600 AND energy < 10'
        with lock:
            result = sql.execute(query2, False, True, cursor=cursor)

        query3 = ''

        for car_s in result:
            index, nalog, owner = car_s
            car = motos[index]
            if nalog + car["nalog"] > car['limit']:
                pass
            else:
                query3 += f'UPDATE moto SET nalog = nalog + {car["nalog"]}, ' \
                          f'last = {time.time()}, energy = energy + 1 WHERE owner = {owner};\n'
        if query3 != '':
            with lock:
                sql.executescript(query3, True, False, cursor=cursor)
    except Exception as ex:
        print('moto_check:', ex)


async def btc_check():
    try:
        cursor = sql.conn.cursor()
        with lock:
            query3 = f'UPDATE bitcoin SET nalog = nalog + stock_nalog, ' \
                     f'last = {time.time()}, balance = ROUND(balance + stock_doxod * videocards) WHERE last is NOT NULL AND ({time.time()} - last) >= 3600 AND stock_nalog*11 >= nalog'
            sql.executescript(query3, True, False, cursor=cursor)
    except Exception as ex:
        print('btc_check:', ex)


async def btc_change():
    x = bitcoin_price() * float(f'0.0{random.randint(0, 5)}')
    now = random.choice([int(bitcoin_price() + x), int(bitcoin_price() - x)])
    if now != bitcoin_price():
        await set_bitcoin_price(now)

    x = euro_price() * float(f'0.0{random.randint(0, 5)}')
    now = random.choice([int(euro_price() + x), int(euro_price() - x)])
    if now != euro_price():
        await set_euro_price(now)

    x = uah_price() * float(f'0.0{random.randint(0, 5)}')
    now = random.choice([int(uah_price() + x), int(uah_price() - x)])
    if now != uah_price():
        await set_uah_price(now)


name_by_index = ['cars', 'airplanes', 'houses', 'businesses',
                 'moto', 'vertoleti', 'yaxti', 'bitcoin']


async def city_check():
    try:
        cursor = sql.conn.cursor()

        try:
            query3 = f"UPDATE city SET workers=CAST (water->'2'->>'work_place' AS INTEGER) * CAST (water->'2'->>'count_build' AS INTEGER)" \
                     f" + CAST (water->'1'->>'work_place' AS INTEGER) * CAST (water->'1'->>'count_build' AS INTEGER)+ " \
                     f"CAST (energy->'2'->>'work_place' AS INTEGER) * CAST (energy->'2'->>'count_build' AS INTEGER)" \
                     f"+ CAST (energy->'1'->>'work_place' AS INTEGER) * CAST (energy->'1'->>'count_build' AS INTEGER) " \
                     f" WHERE happynes > 20;"
            query3 += f"UPDATE city SET kazna=kazna+((taxes/100) * workers) WHERE happynes > 20;"
            with lock:
                sql.executescript(query3, True, False, cursor=cursor)
        except Exception as ex:
            print('city_check (kazna,workers):', ex)
        #########################################################################################
        try:
            query5 = f"UPDATE city SET citizens = CAST (house->'2'->>'capacity' AS INTEGER)* CAST (house->'2'->>'count_build' AS INTEGER) " \
                     f"+ CAST (house->'1'->>'capacity' AS INTEGER) * CAST (house->'1'->>'count_build' AS INTEGER)" \
                     f"WHERE happynes > 20;"
            with lock:
                sql.executescript(query5, True, False, cursor=cursor)
        except Exception as ex:
            print('city_check capacity:', ex)
        ##############################################################################################

        query7 = f" UPDATE city SET happynes = 101-taxes-{random.uniform(0.01, 0.99)};"
        with lock:
            sql.executescript(query7, True, False, cursor=cursor)
    except (Exception, Error) as error:
        print('city_check:', error)


async def autonalog_check():
    with lock:
        query = 'SELECT id, bank FROM users WHERE autonalogs IS TRUE AND bank > 1000'
        data = sql.execute(query, False, True)
        query2 = ''
        for user_id, bank in data:
            owner = user_id
            data = []
            for i in name_by_index:
                x = sql.execute(f'SELECT nalog FROM {i} WHERE owner = {owner}',
                                False, True)

                data.append(x[0][0] if len(x) > 0 else None)
            if len(data) == 0:
                continue
            nalog = data
            nalog_summ = sum(i for i in nalog if i is not None)

            if nalog_summ > bank or nalog_summ == 0:
                continue

            query2 += f'UPDATE users SET bank = bank - {nalog_summ} WHERE id = {owner};\n'

            for index, value in enumerate(nalog):
                if value is not None:
                    query2 += f'UPDATE {name_by_index[index]} SET nalog = 0 WHERE owner = {owner};\n'
        if query2 != '':
            sql.executescript(query2, True, False)


async def autopromo_handler():
    try:
        price = random.randint(100000, 200000)
        acts = random.randint(1, 4)
        name = 'pegas'
        name += ''.join(
            random.choice(string.ascii_letters + '0123456789_') for _ in range(random.randint(6, 10))).lower()
        if name not in all_promo():
            try:
                Promocode.create(name=name,
                                 activations=acts,
                                 summ=price,
                                 xd=1,
                                 id=101010)
                await bot.send_message(
                    text=f'🪄 Промокод <code>{name}</code>\n➖➖➖➖➖➖➖➖\n 💰 Сумма {to_str(price)}\n➖➖➖➖➖➖➖➖\n 👤 Активаций {acts} шт.\n',
                    chat_id=config.channel_offical)
            except Exception as e:
                print('autopromo_handler1:', e)
    except Exception as e:
        print('autopromo_handler:', e)


async def auction_handler():
    try:

        cursor = sql.conn.cursor()

        query2 = f'SELECT seller, uuid4, count, price, costumers, message_id FROM auction WHERE time is NOT NULL AND ' \
                 f'({int(time.time())} - time) >= ' \
                 f'900'
        with lock:
            result = sql.execute(query2, False, True, cursor=cursor)

        query3 = ''

        for lot_s in result:
            seller, uuid4, count, price, costumers, message_id = lot_s
            query3 += f"DELETE FROM auction WHERE uuid4 = '{uuid4}';"
            if costumers == None:
                query3 += f'UPDATE users SET coins = coins + {count} ' \
                          f'WHERE id = {seller};\n'
                with suppress(TelegramBadRequest):
                    await bot.send_message(
                        text=f'⚖️ Ваш лот №{uuid4} \nНе был продан за {to_str(price)}\n',
                        chat_id=seller)

                with suppress(TelegramBadRequest):
                    await bot.edit_message_text(
                        text=
                        f'<b>⚖️ Лот №{uuid4} не был продан</b>\n'
                        f'Предмет:<b> Коины x{count} 🪙</b>\n'
                        f'Ставка: <b>{to_str(price)}</b>\n'
                        f'<b>Владелец лота:</b> {User(id=seller).link} \n',
                        chat_id=config.channel_auction, message_id=message_id, disable_web_page_preview=True)

            else:
                query3 += f"UPDATE users SET balance=balance + {price - int((float(price) * 0.05))} WHERE id = {seller};"
                query3 += f'UPDATE users SET coins = coins + {count} WHERE id = {costumers};\n'
                with suppress(TelegramBadRequest):
                    await bot.send_message(
                        text=f'⚖️ Твоя ставка 🪙x{count} стала победной за лот Лот №{uuid4}\n',
                        chat_id=costumers)

                with suppress(TelegramBadRequest):
                    await bot.send_message(
                        text=f'⚖️ Ваш лот №{uuid4} был продан за {to_str(price)}\n'
                             f'💰 Ты получил {to_str(price - int((float(price) * 0.05)))}<i>(Комиссия 5%)</i>',
                        chat_id=seller)
                with suppress(TelegramBadRequest):
                    await bot.edit_message_text(
                        text=
                        f'<b>⚖️ Лот №{uuid4} продан</b>\n'
                        f'Предмет:<b> Коины x{count} 🪙</b>\n'
                        f'Победившая ставка:<b> {to_str(price)}</b>\n'
                        f'<b>Владелец лота:</b> {User(id=seller).link} \n'
                        f'<b>Победитель аукциона:</b> {User(id=costumers).link}\n',
                        chat_id=config.channel_auction, message_id=message_id, disable_web_page_preview=True)

        if query3 != '':
            with lock:
                sql.executescript(query3, True, False, cursor=cursor)
    except Exception as e:
        print('auction_s:', e)


async def boss_spavn():
    with lock:
        bosse = sql.execute("SELECT * FROM bosses", fetch=True)
    ids_bosse = [1, 2, 3, 4, 5, 6]
    for boss in bosse:
        boss_id, hp = boss
        ids_bosse.remove(boss_id)
    if ids_bosse:
        id = random.choice(ids_bosse)
        res = (id, bosses[id]['begin_hp'])
        sql.insert_data([res], table='bosses')


async def boss_check():
    with lock:
        bosses_sql = sql.execute("SELECT * FROM bosses", fetch=True)

    if not bosses_sql:
        return
    for bosse in bosses_sql:
        boss_id, hp = bosse
        if hp <= 0:
            sql.delete_data(name=boss_id, title_name='id', table='bosses')
            top_damage = sql.execute(
                f"SELECT user_id,damage FROM user_bosses WHERE boss_id ={boss_id} ORDER BY damage DESC;",
                fetch=True)
            index = 0
            for user_top in top_damage:
                user_id, damage = user_top
                index += 1
                tokens = random.randint(20, 40)
                fragments = random.randint(10, 25)
                armory_inv = ArmoryInv(user_id)
                armory_inv.editmany(tokens=armory_inv.tokens + tokens, fragments=armory_inv.fragments + fragments)
                if index == 1:
                    user = User(id=user_id)
                    user.cases = list(user.cases)
                    user.set_case(item_id=3, x=1)
                    with suppress(TelegramBadRequest):
                        await bot.send_message(user_id,
                                               text=f'За убийство босса {bosses[boss_id]["name"]} ты получаешь\n'
                                                    f'🎁 {item_case[3]["name"]}, x{tokens}💠 и x{fragments}💦')
                elif index == 2:
                    user = User(id=user_id)
                    user.cases = list(user.cases)
                    user.set_case(item_id=2, x=1)
                    with suppress(TelegramBadRequest):
                        await bot.send_message(user_id,
                                               text=f'За убийство босса {bosses[boss_id]["name"]} ты получаешь\n'
                                                    f'🎁 {item_case[2]["name"]}, x{tokens}💠 и x{fragments}💦')
                elif index == 3:
                    user = User(id=user_id)
                    user.cases = list(user.cases)
                    user.set_case(item_id=1, x=1)
                    with suppress(TelegramBadRequest):
                        await bot.send_message(user_id,
                                               text=f'За убийство босса {bosses[boss_id]["name"]} ты получаешь\n'
                                                    f'🎁 {item_case[1]["name"]}, x{tokens}💠 и x{fragments}💦')
                else:
                    with suppress(TelegramBadRequest):
                        await bot.send_message(user_id,
                                               text=f'За убийство босса {bosses[boss_id]["name"]} ты получаешь\n'
                                                    f'x{tokens}💠 и x{fragments}💦')
            sql.execute(f"DELETE FROM user_bosses WHERE boss_id ={boss_id} ", commit=True)


job_defaults = {
    'coalesce': False,
    'max_instances': 3
}
shedualer = AsyncIOScheduler(job_defaults=job_defaults)

shedualer.add_job(boss_check, 'cron', minute='*', misfire_grace_time=1000)

shedualer.add_job(boss_spavn, 'interval', hours=3, misfire_grace_time=3600)

shedualer.add_job(auction_handler, 'cron', minute='*', misfire_grace_time=1000)

shedualer.add_job(autopromo_handler, 'interval', hours=24, misfire_grace_time=86400)

shedualer.add_job(city_check, 'cron', minute='*', misfire_grace_time=1000)

shedualer.add_job(limit_check, 'cron', minute='*', misfire_grace_time=1000)

shedualer.add_job(deposit_check, 'cron', minute='*', misfire_grace_time=1000)

shedualer.add_job(autonalog_check, 'cron', minute='*', misfire_grace_time=1000)

shedualer.add_job(houses_check, 'cron', minute='*', misfire_grace_time=1000)

shedualer.add_job(businesses_check, 'cron', minute='*', misfire_grace_time=1000)

shedualer.add_job(cars_check, 'cron', minute='*', misfire_grace_time=1000)

shedualer.add_job(yaxti_check, 'cron', minute='*', misfire_grace_time=1000)

shedualer.add_job(vertoleti_check, 'cron', minute='*', misfire_grace_time=1000)

shedualer.add_job(airplanes_check, 'cron', minute='*', misfire_grace_time=1000)

shedualer.add_job(moto_check, 'cron', minute='*', misfire_grace_time=1000)

shedualer.add_job(btc_check, 'cron', minute='*', misfire_grace_time=1000)

shedualer.add_job(check_jobs, 'cron', minute='*', misfire_grace_time=1000)

shedualer.add_job(btc_change, 'cron', hour='*', misfire_grace_time=1000)

shedualer.start()
