import decimal
import time
from contextlib import suppress
from datetime import datetime, timedelta

import asyncio

from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from psycopg2 import Error, OperationalError

import config
from config import donates, set_bitcoin_price, bitcoin_price, uah_price, set_uah_price, set_euro_price, euro_price
from handlers.users.clan.clan_rob import name_robs

from loader import bot
from utils.bosses import bosses

from utils.items.items import item_case

from utils.main.cash import to_str
from utils.main.db import sql

from utils.main.users import User
from utils.promo.promo import Promocode, all_promo

import random
import string

from utils.weapons.swords import ArmoryInv

lock = asyncio.Lock()


async def limit_check():
    try:
        async with lock:
            cursor = sql.conn.cursor()
            query = ''
            data = sql.execute('SELECT id, donate_source FROM users WHERE last_vidacha'
                               f" IS NOT NULL AND current_timestamp - last_vidacha >= interval '1 day';",
                               False, True)
        if data != None:
            for i in data:
                if i[1] != None:
                    x = i[1].split(',')
                    item = donates[int(x[0])]
                    query += f"UPDATE users SET limitvidach={item['limitvidach']},last_vidacha='{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}' WHERE id = {i[0]};\n"
            if query != '':
                async with lock:
                    sql.executescript(cursor=cursor,
                                      commit=True,
                                      query=query)
    except (Exception, Error, OperationalError) as ex:
        print('limit_check:', ex)


async def deposit_check():
    try:
        async with lock:
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
            async with lock:
                sql.executescript(cursor=cursor,
                                  commit=True,
                                  query=query)
        query = f'UPDATE users SET deposit_date = {time.time()}, deposit = deposit +' \
                'cast(ROUND(deposit * (1)/' \
                '100) as integer)' \
                f' WHERE deposit_date IS NOT ' \
                f'NULL AND ' \
                f'({time.time()} - deposit_date) >= 43200 ;\n'

        async with lock:
            sql.executescript(cursor=cursor,
                              commit=True,
                              query=query)
        query = f'UPDATE users SET credit_time = {time.time()}, \n' \
                f'bank = ' \
                f'CASE WHEN bank - cast(ROUND(credit / 10,0) as int)>=0  THEN bank - cast(ROUND(credit / 10,0) as int) ELSE bank END ,\n' \
                f'balance = ' \
                f'CASE WHEN NOT (bank - cast(ROUND(credit / 10,0) as int)>=0) AND (balance - cast(ROUND(credit / 10,0) as int)>=0) THEN balance - cast(ROUND(credit / 10,0) as int) ELSE balance END ' \
                f'WHERE credit_time IS NOT NULL AND ({time.time()} - credit_time) >= 0;\n'

        query += f'UPDATE users SET energy = energy + 1, energy_time = {time.time()}' \
                 f' WHERE energy < 20 AND energy_time IS NOT NULL AND (' \
                 f'{time.time()} - energy_time) >= 600;'
        async with lock:
            sql.executescript(query, commit=True, cursor=cursor)
    except Exception as ex:
        print('deposit_check:', ex)


async def check_jobs():
    try:
        async with lock:
            cursor = sql.conn.cursor()
        query = f'UPDATE users SET level = level + 1, job_time=NULL WHERE job_time IS NOT NULL AND ({time.time()} - job_time) >= ' \
                f'1;\n'

        query += f'UPDATE users SET work_time = {time.time()}, ' \
                 f'bank =  ' \
                 f'CASE ' \
                 f'WHEN job_index=1 THEN bank + 120000 ' \
                 f'WHEN job_index=2 THEN bank + 90000 ' \
                 f'WHEN job_index=3 THEN bank + 85000 ' \
                 f'WHEN job_index=4 THEN bank + 64500 ' \
                 f'WHEN job_index=5 THEN bank + 53500 ' \
                 f'WHEN job_index=6 THEN bank + 42500 ' \
                 f'WHEN job_index=7 THEN bank + 31500 ' \
                 f'WHEN job_index=8 THEN bank + 20500 ' \
                 f'ELSE bank END \n' \
                 f'WHERE  work_time' \
                 f' IS NOT NULL AND job_index > 0 AND ({time.time()} - ' \
                 f'work_time) >= 3600'
        async with lock:
            sql.executescript(cursor=cursor,
                              query=query,
                              commit=True,
                              fetch=False)
    except Exception as ex:
        print('check_jobs:', ex)


async def cars_check():
    try:
        cursor = sql.conn.cursor()
        async with lock:
            query3 = f'UPDATE cars SET nalog = nalog + stock_nalog, ' \
                     f'last = {time.time()}, energy = energy + 1 WHERE  last is NOT NULL AND ({time.time()} - last) >= 3600 AND stock_nalog*11 >= nalog AND energy < 10'

            sql.executescript(query3, True, False, cursor=cursor)
    except Exception as ex:
        print('cars_check:', ex)


async def houses_check():
    try:
        cursor = sql.conn.cursor()
        async with lock:
            query3 = f'UPDATE houses SET nalog = nalog + stock_nalog, ' \
                     f'last = {time.time()}, cash = ROUND(cash + stock_doxod) WHERE arenda IS TRUE AND last is NOT NULL AND ({time.time()} - last) >= 3600 AND stock_nalog*11 >= nalog'
            sql.executescript(query3, True, False, cursor=cursor)
    except Exception as ex:
        print('businesses_check:', ex)


async def businesses_check():
    try:
        cursor = sql.conn.cursor()
        async with lock:
            query3 = f'UPDATE businesses SET nalog = nalog + stock_nalog, ' \
                     f'last = {time.time()}, cash = ROUND(cash + stock_doxod) WHERE last is NOT NULL AND ({time.time()} - last) >= 3600 AND stock_nalog*11 >= nalog'
            sql.executescript(query3, True, False, cursor=cursor)
    except Exception as ex:
        print('businesses_check:', ex)


async def yaxti_check():
    try:
        cursor = sql.conn.cursor()
        async with lock:
            query3 = f'UPDATE yaxti SET nalog = nalog + stock_nalog, ' \
                     f'last = {time.time()}, energy = energy + 1 WHERE last is NOT NULL AND ({time.time()} - last) >= 3600 AND stock_nalog*11 >= nalog AND energy < 10'

            sql.executescript(query3, True, False, cursor=cursor)
    except Exception as ex:
        print('yaxti_check:', ex)


async def vertoleti_check():
    try:
        cursor = sql.conn.cursor()
        async with lock:
            query3 = f'UPDATE vertoleti SET nalog = nalog + stock_nalog, ' \
                     f'last = {time.time()}, energy = energy + 1 WHERE last is NOT NULL AND ({time.time()} - last) >= 3600 AND stock_nalog*11 >= nalog AND energy < 10'

            sql.executescript(query3, True, False, cursor=cursor)
    except Exception as ex:
        print('vertoleti_check:', ex)


async def airplanes_check():
    try:

        cursor = sql.conn.cursor()
        async with lock:
            query3 = f'UPDATE airplanes SET nalog = nalog + stock_nalog, ' \
                     f'last = {time.time()}, energy = energy + 1 WHERE last is NOT NULL AND ({time.time()} - last) >= 3600 AND stock_nalog*11 >= nalog AND energy < 10'

            sql.executescript(query3, True, False, cursor=cursor)
    except Exception as ex:
        print('airplanes_check:', ex)


async def moto_check():
    try:
        cursor = sql.conn.cursor()
        async with lock:
            query3 = f'UPDATE moto SET nalog = nalog + stock_nalog, ' \
                     f'last = {time.time()}, energy = energy + 1 WHERE  last is NOT NULL AND ({time.time()} - last) >= 3600 AND stock_nalog*11 >= nalog AND energy < 10'

            sql.executescript(query3, True, False, cursor=cursor)
    except Exception as ex:
        print('moto_check:', ex)


async def btc_check():
    try:
        cursor = sql.conn.cursor()
        async with lock:
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


async def city_check():
    try:
        cursor = sql.conn.cursor()

        try:
            query3 = f"UPDATE city SET workers=" \
                     "(CAST(water #>> '{2,work_place}' AS INTEGER) * CAST(water #>> '{2,count_build}' AS INTEGER))" \
                     "  + (CAST(water #>> '{1,work_place}' AS INTEGER) * CAST(water #>> '{1,count_build}' AS INTEGER))" \
                     "  + (CAST(energy #>> '{2,work_place}' AS INTEGER) * CAST(energy #>> '{2,count_build}' AS INTEGER))" \
                     "  + (CAST(energy #>> '{1,work_place}' AS INTEGER) * CAST(energy #>> '{1,count_build}' AS INTEGER))" \
                     f" WHERE happynes > 20 AND current_timestamp - last_online < interval '1 day';"
            query3 += f"UPDATE city SET kazna=ROUND(kazna+(CAST(taxes AS DECIMAL) / 100 * workers)) WHERE happynes > 20  AND current_timestamp - last_online < interval '1 day';"
            async with lock:
                sql.executescript(query3, True, False, cursor=cursor)
        except Exception as ex:
            print('city_check (kazna,workers):', ex)
        #########################################################################################
        try:
            query5 = f"UPDATE city SET citizens = CAST (house->'2'->>'capacity' AS INTEGER)* CAST (house->'2'->>'count_build' AS INTEGER) " \
                     f"+ CAST (house->'1'->>'capacity' AS INTEGER) * CAST (house->'1'->>'count_build' AS INTEGER)" \
                     f"WHERE happynes > 20 AND current_timestamp - last_online < interval '1 day';"
            async with lock:
                sql.executescript(query5, True, False, cursor=cursor)
        except Exception as ex:
            print('city_check capacity:', ex)
        ##############################################################################################

        query7 = f" UPDATE city SET happynes = 101-taxes-{random.uniform(0.01, 0.99)} WHERE  current_timestamp - last_online < interval '1 day';"
        async with lock:
            sql.executescript(query7, True, False, cursor=cursor)
    except (Exception, Error) as error:
        print('city_check:', error)


name_by_index = ['cars', 'airplanes', 'houses', 'businesses',
                 'moto', 'vertoleti', 'yaxti', 'bitcoin']


async def autonalog_check():
    async with lock:
        query = 'SELECT id, bank FROM users WHERE autonalogs IS TRUE AND bank > 1000'
        data = sql.execute(query, False, True)

        update_queries = []
        delete_queries = []

        for user_id, bank in data:
            owner = user_id
            nalog_summ = 0
            for i in name_by_index:
                x = sql.execute(f'SELECT nalog FROM {i} WHERE owner = %s',
                                data=owner, fetch=True)

                if x and x[0][0] is not None:
                    nalog_summ += x[0][0]
                    delete_queries.append((i, owner))

            if nalog_summ <= bank and nalog_summ != 0:
                update_queries.append((nalog_summ, owner))

        if update_queries:

            query = "UPDATE users SET bank = bank - %s WHERE id = %s;"
            query2 = 'UPDATE %s SET nalog = 0 WHERE owner = %s;'
            curs = sql.conn.cursor()
            curs.executemany(query, update_queries)
            for table_name, owner in delete_queries:
                dynamic_query = query2 % (table_name, owner)
                curs.execute(dynamic_query)
            sql.commit()


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
        async with lock:
            result = sql.execute(query2, False, True, cursor=cursor)
        if not result:
            return
        query3 = ''

        for lot_s in result:
            seller, uuid4, count, price, costumers, message_id = lot_s
            query3 += f"DELETE FROM auction WHERE uuid4 = '{uuid4}';"
            if costumers == None:
                query3 += f'UPDATE users SET coins = coins + {count} ' \
                          f'WHERE id = {seller};\n'
                with suppress(TelegramBadRequest, TelegramForbiddenError):
                    await bot.send_message(
                        text=f'⚖️ Ваш лот №{uuid4} \nНе был продан за {to_str(price)}\n',
                        chat_id=seller)

                with suppress(TelegramBadRequest, TelegramForbiddenError):
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
                with suppress(TelegramBadRequest, TelegramForbiddenError):
                    await bot.send_message(
                        text=f'⚖️ Твоя ставка 🪙x{count} стала победной за лот Лот №{uuid4}\n',
                        chat_id=costumers)

                with suppress(TelegramBadRequest, TelegramForbiddenError):
                    await bot.send_message(
                        text=f'⚖️ Ваш лот №{uuid4} был продан за {to_str(price)}\n'
                             f'💰 Ты получил {to_str(price - int((float(price) * 0.05)))}<i>(Комиссия 5%)</i>',
                        chat_id=seller)
                with suppress(TelegramBadRequest, TelegramForbiddenError):
                    await bot.edit_message_text(
                        text=
                        f'<b>⚖️ Лот №{uuid4} продан</b>\n'
                        f'Предмет:<b> Коины x{count} 🪙</b>\n'
                        f'Победившая ставка:<b> {to_str(price)}</b>\n'
                        f'<b>Владелец лота:</b> {User(id=seller).link} \n'
                        f'<b>Победитель аукциона:</b> {User(id=costumers).link}\n',
                        chat_id=config.channel_auction, message_id=message_id, disable_web_page_preview=True)

        if query3 != '':
            async with lock:
                sql.executescript(query3, True, False, cursor=cursor)
    except Exception as e:
        print('auction_s:', e)


async def boss_spavn():
    async with lock:
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
    async with lock:
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

                if index <= 3:
                    user = User(id=user_id)
                    case_index = 4 - index
                    case_count_key = f'{case_index}, count'

                    sql.execute(
                        "UPDATE users SET cases = jsonb_set(cases, "
                        f"'{{{case_count_key}}}', "
                        f"to_jsonb((cases->'{case_count_key}'->>'count')::int + 1)::text::jsonb) "
                        f"WHERE id = {user.id}",
                        commit=True
                    )

                    with suppress(TelegramBadRequest, TelegramForbiddenError):
                        await bot.send_message(user_id,
                                               text=f'За убийство босса {bosses[boss_id]["name"]} ты получаешь\n'
                                                    f'🎁 {item_case[case_index]["name"]}, x{tokens}💠 и x{fragments}💦'
                                               )

                else:
                    with suppress(TelegramBadRequest, TelegramForbiddenError):
                        await bot.send_message(user_id,
                                               text=f'За убийство босса {bosses[boss_id]["name"]} ты получаешь\n'
                                                    f'x{tokens}💠 и x{fragments}💦'
                                               )

            sql.execute(f"DELETE FROM user_bosses WHERE boss_id = {boss_id}", commit=True)


async def clanwarprepare_check():
    async with lock:
        sql.execute(
            f"UPDATE ClanWars SET prepare=False WHERE time_war IS NOT NULL AND time_war - current_timestamp <= interval '3 hours'",
            commit=True)


async def clanwarfind_check():
    async with lock:
        clans = sql.execute(f"SELECT * FROM ClanWarFind WHERE status='FINDING'",
                            fetch=True)

    if not clans:
        return

    clans_groups = [clans[i:i + 2] for i in range(0, len(clans), 2)]

    for group in clans_groups:
        if len(group) % 2 != 0:
            continue
        dt = datetime.now()
        time_war = dt + timedelta(hours=6)
        res = (group[0][3], group[1][3], group[0][4], group[1][4], 0, 0, True,
               time_war.strftime('%d-%m-%Y %H:%M:%S'))
        len_title = "%s," * (len(list(res)) - 1) + "%s"
        sql.get_cursor().execute(f"INSERT INTO ClanWars VALUES(DEFAULT,{len_title})", res)
        sql.execute(
            f"UPDATE ClanWarFind SET end_time='{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}',status='FINDED' WHERE clan_id={group[0][3]};"
            f"UPDATE ClanWarFind SET end_time='{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}',status='FINDED' WHERE clan_id={group[1][3]};",
            commit=True)
        owner = sql.execute(f"SELECT owner FROM Clans WHERE id={group[0][3]}",
                            fetchone=True)[0]
        owner2 = sql.execute(f"SELECT owner FROM Clans WHERE id={group[1][3]}",
                             fetchone=True)[0]
        with suppress(TelegramBadRequest):
            await bot.send_message(chat_id=owner2, text='[КЛАНОВАЯ ВОЙНА]\n'
                                                        f' Война началась! Противник - «{group[0][4]}» ⚔\n'
                                                        '➖ У Вас есть 3 часа на начальную подготовку.\n'
                                                        '➖ Участвуйте в одиночных боях и получайте дополнительные награды! \n',
                                   disable_web_page_preview=True)
        with suppress(TelegramBadRequest):
            await bot.send_message(chat_id=owner, text='[КЛАНОВАЯ ВОЙНА]\n'
                                                       f' Война началась! Противник - «{group[1][4]}» ⚔\n'
                                                       '➖ У Вас есть 3 часа на начальную подготовку.\n'
                                                       '➖ Участвуйте в одиночных боях и получайте дополнительные награды! \n',
                                   disable_web_page_preview=True)


async def clanwars_check():
    async with lock:
        clan_sql = sql.execute(
            f"SELECT id_first, id_second, name_first, name_second,rating_first,rating_second FROM ClanWars WHERE time_war IS NOT NULL "
            f"AND prepare = False "
            f"AND time_war - current_timestamp <= interval '6 hours'",
            fetch=True)
    if not clan_sql:
        return

    for clan in clan_sql:
        clan_id_first, clan_id_second, name_first, name_second, rating_first, rating_second = clan
        query = ''
        if rating_first > rating_second:
            games = 0
            members_mine = sql.select_data(table='WarParticipants', title='clan_id', name=clan_id_first)
            if members_mine:
                for member in members_mine:
                    games += member['attacks']
            sql.execute(
                f"UPDATE Clans SET win=win+1,last_attack={time.time()},rating = rating + 5000 + {games},kazna = kazna+{150_000_000}  WHERE id={clan_id_first};"
                f"UPDATE Clans SET lose=lose+1,last_attack={time.time()},rating = rating + 1000,kazna = kazna+{50_000_000} WHERE id={clan_id_second};"
                f"UPDATE ClanUsers SET rating = rating + 500 "
                f"FROM WarParticipants WHERE WarParticipants.member_id = ClanUsers.user_id AND ClanUsers.clan_id={clan_id_first};"
                f"UPDATE ClanUsers SET rating = rating + 100 "
                f"FROM WarParticipants WHERE WarParticipants.member_id = ClanUsers.user_id AND ClanUsers.clan_id={clan_id_second}",
                commit=True)
            user_ids = sql.execute(query=f'SELECT user_id FROM ClanUsers WHERE clan_id={clan_id_first}', commit=False,
                                   fetch=True)
            for user in user_ids:
                query += \
                    "UPDATE users SET cases = jsonb_set(cases, '{5, count}', " \
                    f"to_jsonb((cases->'5'->>'count')::int + 1)::text::jsonb) WHERE id={user['user_id']};"
                with suppress(TelegramBadRequest, TelegramForbiddenError):
                    await bot.send_message(user[0], text='⚔️[КЛАНОВАЯ ВОЙНА] Результаты:\n'
                                                         f'🏅 Поздравляю с победой над кланом {name_first}!\n'
                                                         '🎁 Выигрышные призы:\n'
                                                         '🔥 Рейтинг клана: +5.000 ед.\n'
                                                         '💰 Валюта: 150.000.000$\n'
                                                         '👑 Рейтинг: +500 ед.\n'
                                                         '🥇 Выигрышный кейс (1x)\n')
                await asyncio.sleep(0.5)
            user_ids2 = sql.execute(query=f'SELECT user_id FROM ClanUsers WHERE clan_id={clan_id_second}', commit=False,
                                    fetch=True)
            for user in user_ids2:
                query += \
                    "UPDATE users SET cases = jsonb_set(cases, '{6, count}', " \
                    f"to_jsonb((cases->'6'->>'count')::int + 1)::text::jsonb) WHERE id={user['user_id']};"
                with suppress(TelegramBadRequest, TelegramForbiddenError):
                    await bot.send_message(user[0], text='⚔️[КЛАНОВАЯ ВОЙНА] Результаты:\n'
                                                         '▶️ К сожалению, Ваш клан проиграл в этой войне!\n'
                                                         '🎁 Утешительные призы:\n'
                                                         '🔥 Рейтинг клана: +1.000 ед.\n'
                                                         '💰 Валюта: 50.000.000$\n'
                                                         '👑 Рейтинг: +100 ед.\n'
                                                         '🥈 Утешительный кейс (1x)\n')
                await asyncio.sleep(0.5)

        elif rating_first < rating_second:

            games = 0
            members_mine = sql.select_data(table='WarParticipants', title='clan_id', name=clan_id_second)
            if members_mine:
                for member in members_mine:
                    games += member['attacks']
            sql.execute(
                f"UPDATE Clans SET win=win+1,last_attack={time.time()},rating = rating + 5000 + {games},kazna = kazna+{150_000_000} WHERE id={clan_id_second};"
                f"UPDATE Clans SET lose=lose+1,last_attack={time.time()},rating = rating + 1000,kazna = kazna+{50_000_000} WHERE id={clan_id_first};"
                f"UPDATE ClanUsers SET rating = rating + 500 "
                f"FROM WarParticipants WHERE WarParticipants.member_id = ClanUsers.user_id AND ClanUsers.clan_id={clan_id_second};"
                f"UPDATE ClanUsers SET rating = rating + 100 "
                f"FROM WarParticipants WHERE WarParticipants.member_id = ClanUsers.user_id AND ClanUsers.clan_id={clan_id_first}",
                commit=True)
            user_ids = sql.execute(query=f'SELECT user_id FROM ClanUsers WHERE clan_id={clan_id_second}', commit=False,
                                   fetch=True)
            for user in user_ids:
                query += \
                    "UPDATE users SET cases = jsonb_set(cases, '{5, count}', " \
                    f"to_jsonb((cases->'5'->>'count')::int + 1)::text::jsonb) WHERE id={user['user_id']};"
                with suppress(TelegramBadRequest, TelegramForbiddenError):
                    await bot.send_message(user['user_id'], text='⚔️[КЛАНОВАЯ ВОЙНА] Результаты:\n'
                                                                 f'🏅 Поздравляю с победой над кланом {name_first}!\n'
                                                                 '🎁 Выигрышные призы:\n'
                                                                 '🔥 Рейтинг клана: +5.000 ед.\n'
                                                                 '💰 Валюта: 150.000.000$\n'
                                                                 '👑 Рейтинг: +500 ед\n.'
                                                                 '🥇 Выигрышный кейс (1x)\n')
                await asyncio.sleep(0.5)
            user_ids2 = sql.execute(query=f'SELECT user_id FROM ClanUsers WHERE clan_id={clan_id_first}', commit=False,
                                    fetch=True)
            for user in user_ids2:
                query += \
                    "UPDATE users SET cases = jsonb_set(cases, '{6, count}', " \
                    f"to_jsonb((cases->'6'->>'count')::int + 1)::text::jsonb) WHERE id={user['user_id']};"
                with suppress(TelegramBadRequest, TelegramForbiddenError):
                    await bot.send_message(user['user_id'], text='⚔️[КЛАНОВАЯ ВОЙНА] Результаты:\n'
                                                                 '▶️ К сожалению, Ваш клан проиграл в этой войне!\n'
                                                                 '🎁 Утешительные призы:\n'
                                                                 '🔥 Рейтинг клана: +1.000 ед.\n'
                                                                 '💰 Валюта: 50.000.000$\n'
                                                                 '👑 Рейтинг: +100 ед.\n'
                                                                 '🥈 Утешительный кейс (1x)\n')
                await asyncio.sleep(0.5)


        else:
            user_ids = sql.execute(
                query=f'SELECT user_id FROM ClanUsers WHERE clan_id={clan_id_second} or clan_id={clan_id_first}',
                commit=False,
                fetch=True)
            for user in user_ids:
                with suppress(TelegramBadRequest, TelegramForbiddenError):
                    await bot.send_message(user[0], text='⚔️[КЛАНОВАЯ ВОЙНА] Результаты:\n'
                                                         '🟰 Ничья Кланы равны по силе !\n')
                await asyncio.sleep(0.5)

        sql.execute(f"DELETE FROM WarParticipants WHERE clan_id = {clan_id_first} or clan_id={clan_id_second};"
                    f"DELETE FROM ClanWars WHERE id_first = {clan_id_first} and id_second={clan_id_second};"
                    f'{query}',
                    commit=True)


async def clanrobprepare_check():
    async with lock:
        sql.execute(
            f"UPDATE ClanRob SET prepare=False,time_rob=NULL WHERE time_rob IS NOT NULL AND time_rob - current_timestamp <= interval '1 second'",
            commit=True)


async def clanrobing_check():
    async with lock:
        sql.execute(
            f"UPDATE ClanRob SET balance = CASE "
            f'WHEN index_rob=1 THEN balance + {round((name_robs[1]["income"] / 60))} * (SELECT COUNT(*) AS count FROM ClanUsers WHERE rob_involved = True AND clan_id = ClanRob.clan_id ) '
            f'WHEN index_rob=2 THEN balance +{round(name_robs[2]["income"] / 60)}  * (SELECT COUNT(*) AS count FROM ClanUsers WHERE rob_involved = True AND clan_id = ClanRob.clan_id )  '
            f'WHEN index_rob=3 THEN balance + {round(name_robs[3]["income"] / 60)}  * (SELECT COUNT(*) AS count FROM ClanUsers WHERE rob_involved = True AND clan_id = ClanRob.clan_id )  '
            f'WHEN index_rob=4 THEN balance + {round(name_robs[4]["income"] / 60)}  * (SELECT COUNT(*) AS count FROM ClanUsers WHERE rob_involved = True AND clan_id = ClanRob.clan_id )  '
            f"END WHERE time_rob IS NOT NULL AND prepare=FALSE",
            commit=True)


async def clanrob_check():
    async with lock:
        clanrob_sql = sql.execute(
            f"SELECT rob_id,clan_id ,index_rob,balance   FROM ClanRob WHERE time_rob IS NOT NULL AND time_rob - current_timestamp <= interval '1 second'"
            f"AND prepare = False ",
            fetch=True)
    if not clanrob_sql:
        return
    for clan in clanrob_sql:
        query = ''
        rob_id, clan_id, index_rob, balance = clan
        user_ids = sql.execute(query=f'SELECT user_id FROM ClanUsers WHERE clan_id={clan_id} and rob_involved=True',
                               commit=False,
                               fetch=True)
        count = sql.execute(f"SELECT COUNT(*) AS count FROM ClanUsers WHERE rob_involved=True AND clan_id={clan_id}",
                            fetchone=True)[0]
        for user in user_ids:
            query += \
                f"UPDATE users SET bank = bank + {round(balance / count)} WHERE id={user['user_id']};" \
                f"UPDATE user_items_rob SET count=0 WHERE user_id={user['user_id']} and count>0;"
            with suppress(TelegramBadRequest, TelegramForbiddenError):
                await bot.send_message(user['user_id'], text='[КЛАНОВОЕ ОГРАБЛЕНИЕ]\n'
                                                             '💰 Ограбление «Магазин» завершено!\n'
                                                             f'💸 Вы заработали {to_str(round(balance / count))}')
            await asyncio.sleep(0.5)
        query += f"UPDATE ClanUsers SET rob_involved=False WHERE clan_id={clan_id};" \
                 f"DELETE FROM ClanRob WHERE rob_id = {rob_id} and clan_id={clan_id};"
    sql.execute(query=query, commit=True)


job_defaults = {
    'coalesce': False,
    'max_instances': 3
}
shedualer = AsyncIOScheduler(job_defaults=job_defaults)

shedualer.add_job(clanrobprepare_check, 'cron', minute='*', misfire_grace_time=1000)
shedualer.add_job(clanrob_check, 'cron', minute='*', misfire_grace_time=1000)
shedualer.add_job(clanrobing_check, 'cron', minute='*', misfire_grace_time=1000)

shedualer.add_job(boss_check, 'cron', minute='*', misfire_grace_time=1000)
shedualer.add_job(boss_spavn, 'interval', hours=3, misfire_grace_time=3600)

shedualer.add_job(clanwars_check, 'cron', minute='*', misfire_grace_time=1000)
shedualer.add_job(clanwarfind_check, 'cron', minute='*', misfire_grace_time=1000)
shedualer.add_job(clanwarprepare_check, 'cron', minute='*', misfire_grace_time=1000)

shedualer.add_job(auction_handler, 'cron', minute='*', misfire_grace_time=1000)

# shedualer.add_job(autopromo_handler, 'interval', hours=24, misfire_grace_time=86400)

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
