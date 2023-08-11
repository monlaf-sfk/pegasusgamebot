import decimal
import random
import re
import time
from contextlib import suppress
from datetime import datetime

from aiogram import flags
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters.callback_data import CallbackData

from aiogram.utils.keyboard import InlineKeyboardBuilder

from filters.users import flood_handler
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton

from loader import bot

from config import bot_name
from keyboard.main import check_ls_kb, settings_notifies_kb, marry_divorce_kb
from keyboard.marries import marrye_kb

from utils.main.cash import get_cash, to_str
from utils.main.db import sql
from utils.main.users import User, Settings
from utils.marries import Marry


class MarryRequest(CallbackData, prefix="marry"):
    user_id: int
    from_whom: int


@flags.throttling_key('default')
async def marries_request_handler(message: Message):
    user = User(id=message.from_user.id)
    try:
        marry = Marry(user_id=message.from_user.id)
    except:
        marry = None
    if marry:
        return await marry_handler(message)
    result = sql.execute(f"SELECT * FROM users_offer WHERE to_whom={message.from_user.id}",
                         fetch=True)
    arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[
        0].lower() else message.text.split()[2:]
    if len(arg) > 0 and arg[0].isdigit() and int(arg[0]) <= len(result):
        arg = int(arg[0]) - 1
        try:
            Marry(user_id=result[arg][1])
            return await message.reply(f'❌ Ошибка. У него\ее уже есть семья!', disable_web_page_preview=True)
        except:
            Marry.create(user1=result[arg][0], user2=result[arg][1])
            await message.reply(f'{user.link}, Вы вышли (замуж\поженились) за игрока {User(id=result[arg][1]).link}',
                                disable_web_page_preview=True)
            sql.execute(
                f"DELETE FROM users_offer WHERE to_whom={result[arg][0]} or from_whom={result[arg][1]}"
                , commit=True)
            sql.execute(
                f"DELETE FROM users_offer WHERE to_whom={result[arg][1]} or from_whom={result[arg][0]}"
                , commit=True)
            settings = Settings(result[arg][1])
            if settings.marry_notifies:
                with suppress(TelegramBadRequest):
                    await bot.send_message(chat_id=result[arg][1],
                                           text=f'[БРАК]\n'
                                                f'▶️ Игрок  {user.link} принял Ваше предложение руки и сердца! 👍🏻\n'
                                                '💞 Для просмотра информации о браке введите «Брак»\n'
                                                '🔔 Для настройки уведомлений введите «Уведомления»\n',
                                           reply_markup=settings_notifies_kb(result[arg][1]),
                                           disable_web_page_preview=True)
            return
    if not result:
        return await message.reply(f'{user.link}, Вам ещё не делали предложения руки и сердца 😔',
                                   disable_web_page_preview=True)
    text = f"{user.link}, найдено {len(result)} предложения брака:\n"
    numbers_emoji = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']
    keyboard = InlineKeyboardBuilder()
    for index, (to_whom, from_whom) in enumerate(result, start=1):
        emoji = ''.join(numbers_emoji[int(i)] for i in str(index))
        text += f'<code>{emoji}</code> {User(id=from_whom).link}\n'
        keyboard.add(
            InlineKeyboardButton(text=f"{emoji}",
                                 callback_data=MarryRequest(from_whom=from_whom, user_id=to_whom).pack())
        )
    text += '\n💞 Для согласия введите «Браки [номер предложения]» 👍🏻'
    return await message.reply(text, reply_markup=keyboard.adjust(2).as_markup(),
                               disable_web_page_preview=True)


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
                to_whom = sql.execute(f"SELECT * FROM users_offer WHERE from_whom={user1.id} and to_whom={user2.id}",
                                      fetchone=True)
                from_whom = sql.execute(f"SELECT * FROM users_offer WHERE from_whom={user2.id} and to_whom={user1.id}",
                                        fetchone=True)
                if from_whom:
                    Marry.create(user1=user1.id, user2=user2.id)

                    await message.reply(
                        f'{user1.link}, Вы вышли (замуж\поженились) за игрока {user2.link}',
                        disable_web_page_preview=True)
                    sql.execute(
                        f"DELETE FROM users_offer WHERE to_whom={user1.id} or from_whom={user2.id}"
                        , commit=True)
                    sql.execute(
                        f"DELETE FROM users_offer WHERE to_whom={user2.id} or from_whom={user1.id}"
                        , commit=True)
                    settings = Settings(user2.id)
                    if settings.marry_notifies:
                        with suppress(TelegramBadRequest):
                            await bot.send_message(chat_id=user2.id,
                                                   text=f'[БРАК]\n'
                                                        f'▶️ Игрок  {user.link} принял Ваше предложение руки и сердца! 👍🏻\n'
                                                        '💞 Для просмотра информации о браке введите «Брак»\n'
                                                        '🔔 Для настройки уведомлений введите «Уведомления»\n',
                                                   reply_markup=settings_notifies_kb(user2.id),
                                                   disable_web_page_preview=True)
                    return
                if to_whom:
                    return await message.reply(
                        f'{user1.link}, Вы уже предлагали игроку {user2.link} выйти (замуж\пожениться) за\на Вас 👍🏻',
                        disable_web_page_preview=True)
                if to_whom and len(to_whom) >= 8:
                    return await message.reply(
                        f'{user1.link},У данного пользователя уже максимально количество предложений',
                        disable_web_page_preview=True)

                data = [(user2.id, user1.id)]
                placeholders = ', '.join(['%s'] * len(data[0]))
                sql.cursor.execute(f"INSERT INTO users_offer VALUES ({placeholders})", data[0])
                sql.commit()
                settings = Settings(user2.id)
                if settings.marry_notifies:
                    with suppress(TelegramBadRequest):
                        await bot.send_message(chat_id=user2.id,
                                               text=f'[БРАК]\n'
                                                    f'💞 Игрок {user1.link} сделал(a) Вам предложение руки и сердца! \n'
                                                    f'❕ Для просмотра информации введите «Браки»\n'
                                                    '🔔 Для настройки уведомлений введите «Уведомления»',
                                               reply_markup=settings_notifies_kb(user2.id),
                                               disable_web_page_preview=True)

            return await message.reply(
                f'✅ Вы успешно предложили {user2.link} (пожениться\выйти замуж)!\n\nЯ уведомлю вас в личке если '
                'он(а) согласится поэтому обязательно напишите мне что-то в лс @pegasusgame_bot',
                disable_web_page_preview=True, reply_markup=check_ls_kb.as_markup())



        elif arg[0].lower() in ['выйти', 'разорвать', 'удалить']:
            if marry is None:
                return await message.reply('❌ У вас нет семьи :(')
            if message.from_user.id in [marry.user1, marry.user2]:
                await message.reply('❓ Вы уверены что хотите развезтись нажмите кнопку для подтверждения\n'
                                    '▶ Кнопка действительна 30 секунд',
                                    reply_markup=marry_divorce_kb(message.from_user.id, time.time()))

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
            settings = Settings(marry.user2 if message.from_user.id == marry.user1 else marry.user1)
            if settings.marry_notifies:
                with suppress(TelegramBadRequest):
                    await bot.send_message(settings.user_id,
                                           f'[БРАК]\n❕ {user.link} снял с брака {to_str(summ)}',
                                           disable_web_page_preview=True)
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

            settings = Settings(marry.user2 if message.from_user.id == marry.user1 else marry.user1)
            if settings.marry_notifies:
                with suppress(TelegramBadRequest):
                    await bot.send_message(settings.user_id,
                                           f'[БРАК]\n❕ {user.link} пополнил брак на {to_str(summ)}',
                                           disable_web_page_preview=True)
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
async def marry_call_handler(call: CallbackQuery, callback_data: MarryRequest):
    try:
        marry = Marry(user_id=call.from_user.id)
    except:
        marry = None
    if marry:
        return await call.message.edit_text(f'❌ У вас уже есть семья!', disable_web_page_preview=True)
    if callback_data.user_id != call.from_user.id:
        return await call.answer(f'🤨 Убери свои шаловливые руки!')
    try:
        Marry(user_id=callback_data.from_whom)
        return await call.message.edit_text(f'❌ Ошибка. У него\ее уже есть семья!', disable_web_page_preview=True)
    except:
        Marry.create(user1=callback_data.from_whom, user2=callback_data.user_id)
        user = User(id=callback_data.user_id)
        await call.message.edit_text(
            f'{user.link}, Вы вышли (замуж\поженились) за игрока {User(id=callback_data.from_whom).link}',
            disable_web_page_preview=True)
        sql.execute(
            f"DELETE FROM users_offer WHERE to_whom={callback_data.from_whom} or from_whom={callback_data.user_id}"
            , commit=True)
        sql.execute(
            f"DELETE FROM users_offer WHERE to_whom={callback_data.user_id} or from_whom={callback_data.from_whom}"
            , commit=True)
        settings = Settings(callback_data.from_whom)
        if settings.marry_notifies:
            with suppress(TelegramBadRequest):
                await bot.send_message(chat_id=callback_data.from_whom,
                                       text=f'[БРАК]\n'
                                            f'▶️ Игрок  {user.link} принял Ваше предложение руки и сердца! 👍🏻\n'
                                            '💞 Для просмотра информации о браке введите «Брак»\n'
                                            '🔔 Для настройки уведомлений введите «Уведомления»\n',
                                       reply_markup=settings_notifies_kb(callback_data.from_whom),
                                       disable_web_page_preview=True)
        return


@flags.throttling_key('default')
async def marry_divorce_handler(call: CallbackQuery):
    divorce, user_id, time_call = call.data.split(":")
    user_id = int(user_id)

    if user_id != call.from_user.id:
        return await call.answer(f'🤨 Убери свои шаловливые руки!')
    if time.time() - float(time_call) > 30:
        with suppress(TelegramBadRequest):
            await call.answer(f'⏳ Срок действия кнопки истек', show_alert=True)
        return
    try:
        marry = Marry(user_id=call.from_user.id)
    except:
        marry = None
    if marry is None:
        with suppress(TelegramBadRequest):
            call.message.edit_text('❌ У вас нет семьи :(')
        return
    with suppress(TelegramBadRequest):
        user2 = User(id=marry.user2 if call.from_user.id == marry.user1 else marry.user1)
        user1 = User(id=marry.user2 if user2.id == marry.user1 else marry.user1)
        user1.edit('balance', user1.balance + round(marry.balance / 2))
        user2.edit('balance', user2.balance + round(marry.balance / 2))
        await call.message.edit_text(f'{user1.link}, Вы развелись с игроком {user2.link} 😟\n'
                                     f'💸 Общий счёт был поделён поровну: +{to_str(round(marry.balance / 2))}',
                                     disable_web_page_preview=True)
        marry.delete()
    settings = Settings(user2.id)
    if settings.marry_notifies:
        with suppress(TelegramBadRequest):
            await bot.send_message(chat_id=user2.id,
                                   text=f'[БРАК]\n'
                                        f'💔 Ваша (жена\муж) «{user1.link}» решил(а) развестись с Вами ☹\n'
                                        f'💸 Общий счёт был поделен поровну: +{to_str(round(marry.balance / 2))}\n'
                                        '🔔 Для настройки уведомлений введите «Уведомления»\n',
                                   reply_markup=settings_notifies_kb(user2.id),
                                   disable_web_page_preview=True)
