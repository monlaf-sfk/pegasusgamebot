from datetime import datetime

from aiogram.types import Message

from utils.main.db import sql
from utils.main.users import User


async def obnyn_handler(message: Message):
    # await message.answer_document(document=InputFile('assets/database.db'),
    #                               caption=f'База за {datetime.now()}')
    query = f"UPDATE users SET balance = 5000, bank = 0, deposit = 0, pets = '', items = '', deposit_date = NULL, " \
            f"bonus ='{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}', lock = FALSE, credit = 0, credit_time = NULL, energy = 10, energy_time =" \
            f"NULL, xp = 0, sell_count = 0, level = 0, job_index = 0, job_time = NULL," \
            f" work_time = NULL, prefix = NULL, last_vidacha = NULL," \
            f" last_rob = NULL, shield_count = 0, autonalogs = FALSE, skin = NULL, health = 100,cases = '',state_ruletka=NULL, bitcoins=0;\n"

    query += 'TRUNCATE TABLE airplanes;\n' \
             'TRUNCATE TABLE bitcoin;\n' \
             'TRUNCATE TABLE businesses;\n' \
             'TRUNCATE TABLE cars;\n' \
             'TRUNCATE TABLE euro;\n' \
             'TRUNCATE TABLE houses;\n' \
             'TRUNCATE TABLE marries;\n' \
             'TRUNCATE TABLE moto;\n' \
             'TRUNCATE TABLE promocodes;\n' \
             'TRUNCATE TABLE uah;\n' \
             'TRUNCATE TABLE vertoleti;\n' \
             'TRUNCATE TABLE city;\n' \
             'TRUNCATE TABLE yaxti;\n' \
             'UPDATE clans SET kazna=0,power=0,rating=0,win=0,lose=0,level=1,last_attack=NULL;\n' \
             "UPDATE clan_users SET items='' , rating=0;\n" \
             "UPDATE other SET bonus=50000 , zarefa=100000,credit_limit=2,credit_percent=2,coin_kurs=100000,donatex2=1;" \
             "UPDATE chat_wdz SET awards=50000;"

    sql.executescript(query, True, False)
    return await message.reply('👨‍🎤 Обнуление прошло успешно!')


async def obnyn_property_handler(message: Message):
    query = 'TRUNCATE TABLE airplanes;\n' \
            'TRUNCATE TABLE cars;\n' \
            'TRUNCATE TABLE moto;\n' \
            'TRUNCATE TABLE vertoleti;\n' \
            'TRUNCATE TABLE yaxti;' \
 \
    sql.executescript(query, True, False)
    return await message.reply('👨‍🎤 Обнуление имущества прошло успешно!')


async def obnyn_user_handler(message: Message):
    # await message.answer_document(document=InputFile('assets/database.db'),
    #                               caption=f'База за {datetime.now()}')
    try:
        arg = message.text.split(' ')
        if len(arg) == 1 and not message.reply_to_message:
            return await message.reply('Используйте: <code>/reset_user {ссылка}</code>')
        elif len(arg) > 1 and arg[1].isdigit():
            try:
                to_user = User(id=arg[1].replace('@', ''))
            except:
                return await message.reply('❌ Ошибка. В БД нету пользователя с таким id!')
        elif len(arg) > 1:
            try:
                to_user = User(username=arg[1].replace('@', ''))
            except:
                return await message.reply('❌ Ошибка. В БД нету пользователя с таким id!')
        elif message.reply_to_message:
            try:
                to_user = User(id=message.reply_to_message.from_user.id)
            except:
                return await message.reply('❌ Ошибка. В БД нету пользователя с таким id!')
        else:
            return await message.reply('Используйте: <code>/reset_user {ссылка\id}</code>')
        query = f"UPDATE users SET balance = 0, bank = 0, deposit = 0, pets = '', items = '', deposit_date = NULL, " \
                f"bonus ='{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}', lock = FALSE, credit = 0, credit_time = NULL, energy = 10, energy_time =" \
                f"NULL, xp = 0, sell_count = 0, level = 0, job_index = 0, job_time = NULL," \
                f" work_time = NULL, prefix = NULL, last_vidacha = NULL," \
                f" last_rob = NULL, shield_count = 0, autonalogs = FALSE, skin = NULL, health = 100,cases = '',state_ruletka=NULL WHERE id={to_user.id};\n"
        query += f'DELETE FROM airplanes WHERE id={to_user.id};\n' \
                 f'DELETE FROM bitcoin WHERE id={to_user.id};\n' \
                 f'DELETE FROM businesses WHERE id={to_user.id};\n' \
                 f'DELETE FROM cars WHERE id={to_user.id};\n' \
                 f'DELETE FROM euro WHERE id={to_user.id};\n' \
                 f'DELETE FROM houses WHERE id={to_user.id};\n' \
                 f'DELETE FROM marries WHERE id={to_user.id};\n' \
                 f'DELETE FROM moto WHERE id={to_user.id};\n' \
                 f'DELETE FROM uah WHERE id={to_user.id};\n' \
                 f'DELETE FROM vertoleti WHERE id={to_user.id};\n' \
                 f'DELETE FROM city WHERE id={to_user.id};\n' \
                 f'DELETE FROM yaxti WHERE id={to_user.id};' \
 \
        sql.executescript(query, True, False)
        return await message.reply(f'Игрок {to_user.link}! Был обнулен', disable_web_page_preview=True)
    except Exception as e:
        print(e)
