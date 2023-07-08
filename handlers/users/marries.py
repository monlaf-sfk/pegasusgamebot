import decimal
import random
import re
import time
from contextlib import suppress
from datetime import datetime

from aiogram import flags
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

from filters.users import flood_handler
from aiogram.types import Message, CallbackQuery

from loader import bot

from config import bot_name
from keyboard.main import marry_kb, check_ls_kb
from keyboard.marries import marrye_kb
from utils.logs import writelog
from utils.main.cash import get_cash, to_str
from utils.main.db import sql
from utils.main.users import User
from utils.marries import Marry


@flags.throttling_key('default')
async def marry_handler(message: Message):
    flood = await flood_handler(message)
    if flood:
        arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[
            0].lower() else message.text.split()[2:]

        try:
            marry = Marry(user_id=message.from_user.id)
        except:
            marry = None

        user = User(id=message.from_user.id)

        if marry is not None:
            if marry.level is None or marry.level == 0:
                marry.level = 1

        if len(arg) == 0 or arg[0].lower() in ['мой', 'моя', 'моё']:
            if marry is None:
                return await message.reply('❌ У вас нет семьи :(')
            user2 = User(id=marry.user2 if message.from_user.id == marry.user1 else marry.user1)
            user1 = User(id=marry.user2 if user2.id == marry.user1 else marry.user1)

            lol = datetime.now() - marry.reg_date
            xd = f'{lol.days} дн.' if lol.days > 0 else f'{int(lol.total_seconds() // 3600)} час.' \
                if lol.total_seconds() > 59 else f'{int(lol.seconds)} сек.'
            text = f'💍 Ваша семья ({user1.link} & {user2.link})\n' \
                   f'👤 Название: <b>{marry.name}</b>\n' \
                   f'📅 Дата обручения: {marry.reg_date} (<code>{xd}</code>)\n' \
                   f'💰 Капитал семьи: {to_str(marry.balance)}\n' \
                   f'👑 LVL: {marry.level}\n'
            return await message.reply(text=text, disable_web_page_preview=True,
                                       reply_markup=marrye_kb.as_markup())
        elif arg[0].lower() in ['создать']:

            if marry and message.from_user.id in [marry.user1, marry.user2]:
                return await message.reply('❌ У вас уже есть семья... ая-яй изменщик(ца)!')
            try:
                user2 = User(id=message.reply_to_message.from_user.id) if message.reply_to_message else User(
                    username=arg[1].replace('@', ''))
            except:
                return await message.reply('❌ Ошибка. Используйте: <code>Брак создать *{ссылка}</code>')
            try:
                user1 = User(id=message.from_user.id)
                user12 = User(id=message.reply_to_message.from_user.id) if message.reply_to_message else User(
                    username=arg[1].replace('@', ''))
                if user1.id == user12.id:
                    return await message.reply('❌ Самовлюленный! Нельзя сам собой заводить брак!')
            except:
                return await message.reply('❌ Ошибка. Используйте: <code>Брак создать *{ссылка}</code>')
            try:
                Marry(user_id=user2.id)
                return await message.reply(f'❌ Ошибка. У {user2.link} уже есть семья!', disable_web_page_preview=True)
            except:
                try:
                    await bot.send_message(chat_id=user2.id,
                                           text=f'[💍] {user.link} предлагает вам жениться!',
                                           reply_markup=marry_kb(user.id, user2.id), disable_web_page_preview=True)
                except TelegramForbiddenError:
                    return await message.reply(f'❌ {user2.link} ниразу не писал в лс боту и я к сожалению не могу '
                                               'отправить ей запрос на свадьбу!', disable_web_page_preview=True)
            return await message.reply(
                f'✅ Вы успешно предложили {user2.link} пожениться!\n\nЯ уведомлю вас в личке если '
                'он(а) согласится поэтому обязательно напишите мне что-то в лс @pegasusgame_bot',
                disable_web_page_preview=True, reply_markup=check_ls_kb.as_markup())

            # await message.reply(f'✅ Вы успешно приютили {user2.link}', disable_web_page_preview=True)
            # await writelog(message.from_user.id, f'Приючение {user2.link}')
            # return

        elif arg[0].lower() in ['выйти', 'разорвать', 'удалить']:
            if marry is None:
                return await message.reply('❌ У вас нет семьи :(')
            if message.from_user.id in [marry.user1, marry.user2]:
                marry.delete()
                await message.reply('✅ Вы успешно удалили семью! Мне очень жаль :(')

                return

        elif arg[0].lower() in ['снять', 'вывести']:
            if marry is None:
                return await message.reply('❌ У вас нет семьи :(')
            summ = 0
            try:
                summ = get_cash(arg[1])
            except:
                pass

            if summ <= 0:
                return await message.reply('❌ Минимум $1')
            if user.payban:
                return await message.reply(f'❌ {user.link},На ваш аккаунт наложено ограничение на переводы !',
                                           disable_web_page_preview=True)
            elif summ > marry.balance:
                return await message.reply('❌ Недостаточно средств на счету семьи!')

            sql.executescript(f'UPDATE users SET balance = balance + {summ} WHERE id = {message.from_user.id};\n'
                              f'UPDATE marries SET balance = balance - {summ} WHERE (user1 = {message.from_user.id}) OR (user2 = {message.from_user.id})',
                              True, False)

            await message.reply(f'✅ Вы успешно сняли {to_str(summ)} с бюджета семьи!')
            await writelog(message.from_user.id, f'Снятие {to_str(summ)} с бюджета семьи')
            return
        elif arg[0].lower() in ['положить', 'вложить', 'пополнить']:
            if marry is None:
                return await message.reply('❌ У вас нет семьи :(')
            summ = 0
            try:
                summ = get_cash(arg[1])
            except:
                pass

            if summ <= 0:
                return await message.reply('❌ Минимум $1')

            elif summ > user.balance:
                return await message.reply('❌ Недостаточно средств на руках!')
            if user.payban:
                return await message.reply(f'❌ {user.link},На ваш аккаунт наложено ограничение на переводы !',
                                           disable_web_page_preview=True)
            sql.executescript(f'UPDATE users SET balance = balance - {summ} WHERE id = {message.from_user.id};\n'
                              f'UPDATE marries SET balance = balance + {summ} WHERE (user1 = {message.from_user.id}) OR (user2 = {message.from_user.id})',
                              True, False)

            await message.reply(f'✅ Вы успешно пополнили бюджет семьи на +{to_str(summ)}')
            await writelog(message.from_user.id, f'Пополнение {to_str(summ)} в бюджет семьи')
            return
        elif arg[0].lower() in ['награда', 'вознаграждение', 'награждение']:
            lol = datetime.now() - marry.reg_date
            if lol.total_seconds() < 7200:
                xd = f'{round((7200 - lol.total_seconds()) / 60)} мин.'
                return await message.reply(f'⌚ Награду с брака можно использовать через : {xd}')
            if marry.last is not None and (decimal.Decimal(time.time()) - marry.last) < 3600:
                return await message.reply('⌚ Вы недавно забирали награду')

            marry.editmany(last=time.time(),
                           balance=marry.balance + 10000 * marry.level)
            await message.reply(f'🎄 В бюджет семьи было начислено +{to_str(10000 * marry.level)}')

            return
        elif arg[0].lower() in ['секс', 'трахать', 'трахаться', 'траханье']:
            if not marry:
                return await message.reply('❌ У вас нет семьи :(')
            lol = datetime.now() - marry.reg_date
            if lol.total_seconds() < 7200:
                xd = f'{round((7200 - lol.total_seconds()) / 60)} мин.'
                return await message.reply(f'⌚ Не так быстро,вы же только начали отношения : {xd}')
            if marry.last_sex is not None and (decimal.Decimal(time.time()) - marry.last_sex) < 3600:
                return await message.reply('⌚ Вы недавно занимались этим делом!')

            summ = random.randint(5000, 25000 * marry.level)

            marry.editmany(last_sex=time.time(),
                           balance=marry.balance + summ)

            user2 = User(id=marry.user2 if message.from_user.id == marry.user1 else marry.user1)

            await message.reply(f'🎄 Вы занялись сэксом с {user2.link} и в бюджет семьи было начислено '
                                f'+{to_str(summ)}', disable_web_page_preview=True)

            return
        elif arg[0].lower() in ['улучш', 'улучшение', 'улучшить']:
            if not marry:
                return await message.reply('❌ У вас нет семьи :(')

            price = 1000000 * (marry.level + 1)
            if user.balance < price:
                return await message.reply(
                    f'💲 Недостаточно денег на руках для улучшения семьи. Нужно: {to_str(price)}')

            query = f'UPDATE users SET balance = balance - {price} WHERE id = {message.from_user.id};\n' \
                    f'UPDATE marries SET level = level + 1 WHERE (user1 = {message.from_user.id}) OR (user2 = {message.from_user.id});'
            sql.executescript(query=query, commit=True, fetch=False)

            return await message.reply(f'✅ Вы улучшили уровень семьи на +1, текущий уровень: {marry.level + 1}')
        elif arg[0].lower() in ['назвать', 'переименовать', 'ник', 'нейм',
                                'название']:
            if not marry:
                return await message.reply('❌ У вас нет семьи :(')

            if marry.level < 3:
                return await message.reply('👑 Нужен 4 лвл чтобы менять название семьи!')

            try:
                name = re.sub('''[@"'%<>💎👨‍🔬🌟⚡👮‍♂➪👾🥲⛏😎👑💖🐟🍆😈🏿🐥👶🏿🇷🇺🇺🇦]''', '', arg[1])
            except:
                return await message.reply('❌ Используйте: <code>Брак назвать {название}</code>')
            if len(name) < 4 or len(name) > 16:
                return await message.reply('❌ Длина больше 16 или меньше 4. Запрещены символы.')

            marry.edit('name', name)

            return await message.reply(f'✅ Вы успешно изменили название семьи на: <b>{name}</b>')

        else:
            return await message.reply('❌ Ошибка. Используйте помощь чтобы узнать команды!')


@flags.throttling_key('default')
async def marry_call_handler(call: CallbackQuery):
    user1 = int(call.data.split('_')[1])
    if str(call.data.split('_')[0]) == 'maccept':
        try:
            Marry(user_id=user1)
            await call.answer('❌ Пользователь уже в браке')
            return await call.message.delete()
        except:
            pass
        try:
            Marry(user_id=call.from_user.id)
            await call.answer('❌ Пользователь уже в браке')
            return await call.message.delete()
        except:
            pass
        try:
            await bot.send_message(chat_id=user1,
                                   text=f'Ура, ваша вторая половинка которой'
                                        f' вы предлагали пожениться приняла запрос на свадьбу!')
        except:
            pass
        Marry.create(user1=user1, user2=call.from_user.id)
        await call.answer('Брак зарегистрирован!')

        with suppress(TelegramBadRequest):
            await call.message.delete()
        return
    else:
        await bot.send_message(chat_id=user1,
                               text=f'К сожелению вам отказали')
        with suppress(TelegramBadRequest):
            return await call.message.delete()
