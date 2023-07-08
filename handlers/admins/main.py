import asyncio
import time
from contextlib import suppress
from datetime import datetime, timedelta
from typing import Optional

from aiogram import flags
from aiogram.exceptions import TelegramBadRequest

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import donates, bot_name, owner_id

from keyboard.main import admin_kb, cancel, remove
from loader import bot
from states.admins import ABD
from utils.main.airplanes import all_airplanes
from utils.main.businesses import all_businesses
from utils.main.cars import all_cars
from utils.main.chat_wdz import Chat_wdz
from utils.main.chats import all_chats
from utils.main.db import sql, timetostr
from utils.main.houses import all_houses
from utils.main.moto import all_moto
from utils.main.users import all_users, all_users_ban
from utils.main.cash import get_cash
import os
import psutil
from threading import Lock
from utils.main.airplanes import Airplane
from utils.main.bitcoin import Bitcoin, all_ferma
from utils.main.businesses import Business
from utils.main.cars import Car
from utils.main.cash import to_str
from utils.main.chats import Chat
from utils.main.db import timetomin
from utils.main.houses import House
from utils.main.moto import Moto

from utils.main.users import User
from utils.main.vertoleti import Vertolet
from utils.main.yaxti import Yaxta
from utils.marries import Marry
from utils.main.vertoleti import all_vertoleti
from utils.main.yaxti import all_yaxti
from utils.marries import all_marries
from utils.promo.promo import all_promo

lock = Lock()


@flags.throttling_key('default')
async def profile_handler_admin(message: Message):
    arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[0].lower() else message.text.split()[
                                                                                                   2:]
    try:
        if len(arg) > 0 and arg[0].isdigit():
            user = User(id=arg[0].replace('@', ''))
        elif len(arg) > 0:
            user = User(username=arg[0].replace('@', ''))
        else:
            user = User(user=message.reply_to_message.from_user)
    except:
        return await bot.send_message(chat_id=message.chat.id,
                                      text='❌ В БД нету данного пользователя!',
                                      disable_web_page_preview=True)
    try:
        marry = Marry(user_id=user.id)
    except:
        marry = None
    try:
        business = Business(user_id=user.id)
    except:
        business = None
    try:
        house = House(user_id=user.id)
    except:
        house = None
    try:
        car = Car(user_id=user.id)
    except:
        car = None
    try:
        yaxta = Yaxta(user_id=user.id)
    except:
        yaxta = None
    try:
        vertolet = Vertolet(user_id=user.id)
    except:
        vertolet = None
    try:
        airplane = Airplane(user_id=user.id)
    except:
        airplane = None
    try:
        moto = Moto(user_id=user.id)
    except:
        moto = None
    try:
        btc = Bitcoin(owner=user.id)
    except:
        btc = None

    text = f'👤 Профиль пользователя: {user.link}\n\n' \
           f'➖➖➖➖➖➖➖➖➖➖➖➖\n' \
           f'• 💸 Баланс: {to_str(user.balance)}\n' \
           f'• 🏦 В банке: {to_str(user.bank)}\n' \
           f'• 💳 Кредит: {to_str(user.credit)}\n' \
           f'• 〽️ Депозит: {to_str(user.deposit)}\n' \
           f'• 🪙 Коины: {user.coins}\n\n' \
           f'➖➖➖➖➖➖➖➖➖➖➖➖\n'
    lol = datetime.now() - user.reg_date
    xd2 = f'{lol.days // 30} месяц{"ев" if lol.days // 30 > 5 else ""}' if lol.days > 30 else f'{lol.days} дней' if lol.days > 0 else f'{int(lol.total_seconds() // 3600)} часов' \
        if lol.total_seconds() > 59 else f'{int(lol.seconds)} секунд'
    xd = f' ({timetomin(int((int(user.energy_time) + 3600) - time.time()))})' if user.energy_time is not None else ''
    text += f'📅 Время в боте: {xd2}\n' \
            f'👥 Рефералы: {user.refs}\n' \
            f'🔒 Кошелёк: {"Закрыт" if user.lock else "Открыт"}\n' \
            f'⚡ Энергия: {user.energy}{xd}\n' \
            f'💡️ XP: {user.xp}\n' \
            f'⭐ BTC: <b>{btc.balance if btc else 0.0}</b>\n' \
        # f'🎫 Скидка: x{user.sell_count}\n' \

    try:
        text += f'⭐ Уровень: <b>{user.level_json.get("name")}</b>({user.level})\n'
    except:
        pass
    try:
        text += f'👻 Работа: <b>{user.job.get("name") if user.job else "Нет ❌"}</b>\n'
    except:
        pass

    text += f'➖➖➖➖➖➖➖➖➖➖➖➖\n' \
            f'💍 Семья: <b>{marry.name if marry and marry.name else "Есть ✅" if marry else "Нет ❌"}</b>\n' \
            f'👨‍💼 Бизнес: <b>{business.name if business else "Нет ❌"}</b>\n' \
            f'🏠 Дом: <b>{house.name if house else "Нет ❌"}</b>\n' \
            f'🏎️ Машина: <b>{car.name if car else "Нет ❌"}</b>\n' \
            f'🛳️ Яхта: <b>{yaxta.name if yaxta else "Нет ❌"}</b>\n' \
            f'🚁 Вертолёт: <b>{vertolet.name if vertolet else "Нет ❌"}</b>\n' \
            f'✈️ Самолёт: <b>{airplane.name if airplane else "Нет ❌"}</b>\n' \
            f'🏍️ Мото: <b>{moto.name if moto else "Нет ❌"}</b>\n' \
            f'🎡 Ферма: <b>{btc.bitcoin.name if btc else "Нет ❌"}</b>\n'
    xd = [business, house, car, yaxta,
          vertolet, airplane,
          moto, btc]
    nalog = sum(i.nalog for i in xd if i)

    text += f'💲 Налог в сумме: {to_str(nalog)}\n'
    text += f'➖➖➖➖➖➖➖➖➖➖➖➖\n' \
            f'{"🚫 Ограничение на переводы" if user.payban else ""}\n' \
            f'{"🚫 Ограничение на смену ника" if user.nickban else ""}\n' \
            f'{"📛 ЧС проекта" if user.ban else ""}\n' \
        if user.payban or user.nickban or user.ban else ''

    await bot.send_message(chat_id=message.chat.id,
                           text=text,
                           disable_web_page_preview=True)


@flags.throttling_key('default')
async def admin_nickname_handler(message: Message):
    arg = message.text.split(' ')
    try:
        if len(arg) == 1:
            return await message.reply(f'👓 Введите никнейм <b>/nick (ник)</b>')
        if len(arg) > 2 and arg[1].isdigit():
            to_user = User(id=arg[1].replace('@', ''))
            to_user.edit('name', arg[2])
            await message.reply(f'✅ Его никнейм успешно изменён на: <code>{to_user.name}</code>')
        elif len(arg) > 2:
            to_user = User(username=arg[1].replace('@', ''))
            to_user.edit('name', arg[2])
            await message.reply(f'✅ Его никнейм успешно изменён на: <code>{to_user.name}</code>')
        elif message.reply_to_message:
            to_user = User(user=message.reply_to_message.from_user)
            to_user.edit('name', arg[1])
            await message.reply(f'✅ Его никнейм успешно изменён на: <code>{to_user.name}</code>')
        else:
            return await message.reply(f'👓 Введите никнейм <b>/nick (ник)</b>')
    except:
        return await message.reply(f'👓 Введите никнейм <b>/nick (ник)</b>')


@flags.throttling_key('default')
async def devidebalance_handler(message: Message):
    arg = message.text.split()[1:]
    if len(arg) == 0:
        return await message.reply('Используйте: <code>Разделить {число} *{ссылка}</code>')

    summ = get_cash(arg[0])
    arg[0] = arg[0].replace('$', '')
    if len(arg) > 1 and arg[1].isdigit():
        to_user = User(id=arg[1].replace('@', ''))
    elif len(arg) > 1:
        to_user = User(username=arg[1].replace('@', ''))
    else:
        to_user = User(user=message.reply_to_message.from_user)

    summ2 = to_user.balance / summ
    to_user.edit('balance', summ2)

    return await message.reply(f'Вы успешно разделили баланс пользователю {to_user.link} на {summ} и его теку'
                               f'щий баланс: {to_str(summ2)}',
                               disable_web_page_preview=True)


@flags.throttling_key('default')
async def multibalance_handler(message: Message):
    arg = message.text.split()[1:]

    if len(arg) < 1:
        return await message.reply('Используйте: <code>Умножить {число} *{ссылка}</code>')

    summ = get_cash(arg[0])
    arg[0] = arg[0].replace('$', '')
    if len(arg) > 1 and arg[1].isdigit():
        to_user = User(id=arg[1].replace('@', ''))
    elif len(arg) > 1:
        to_user = User(username=arg[1].replace('@', ''))
    else:
        to_user = User(user=message.reply_to_message.from_user)

    summ2 = to_user.balance * summ

    to_user.edit('balance', summ2)

    return await message.reply(f'Вы успешно умножили баланс у пользователя {to_user.link} на {summ} и его теку'
                               f'щий баланс: {to_str(summ2)}',
                               disable_web_page_preview=True)


@flags.throttling_key('default')
async def takebalance_handler(message: Message):
    arg = message.text.split()[1:]

    if len(arg) < 1:
        return await message.reply('Используйте: <code>Забрать {сумма} *{ссылка}</code>')

    summ = get_cash(arg[0])
    arg[0] = arg[0].replace('$', '')
    if len(arg) > 1 and arg[1].isdigit():
        to_user = User(id=arg[1].replace('@', ''))
    elif len(arg) > 1:
        to_user = User(username=arg[1].replace('@', ''))
    else:
        to_user = User(user=message.reply_to_message.from_user)

    summ2 = to_user.balance - summ

    to_user.edit('balance', summ2)

    return await message.reply(f'Вы успешно забрали баланс у пользователя {to_user.link} {to_str(summ)} и его теку'
                               f'щий баланс: {to_str(summ2)}',
                               disable_web_page_preview=True)


@flags.throttling_key('default')
async def givebalance_handler(message: Message):
    arg = message.text.split()[1:]

    if len(arg) < 1:
        return await message.reply('Используйте: <code>Выдать {сумма} *{ссылка}</code>')

    summ = get_cash(arg[0])
    arg[0] = arg[0].replace('$', '')
    if len(arg) > 1 and arg[1].isdigit():
        to_user = User(id=arg[1].replace('@', ''))
    elif len(arg) > 1:
        to_user = User(username=arg[1].replace('@', ''))
    else:
        to_user = User(user=message.reply_to_message.from_user)
    summ2 = to_user.balance + summ

    to_user.edit('balance', summ2)

    return await message.reply(f'Вы успешно выдали пользователю {to_user.link} {to_str(summ)} и его теку'
                               f'щий баланс: {to_str(summ2)}',
                               disable_web_page_preview=True)


@flags.throttling_key('default')
async def givebalance_admin_handler(message: Message):
    arg = message.text.split()[1:]
    if len(arg) == 0:
        return await message.reply('Используйте: <code>Выдать {кол-во} *{ссылка}</code>')
    now = datetime.now()
    user = User(user=message.from_user)
    if user.limitvidach <= 0:
        x = (now - user.last_vidacha).total_seconds()
        return await message.reply(f'💓 Лимит выдачи, сброс через: {timetostr(3600 * 24 - x)}')
    try:
        summ = get_cash(arg[0])
        if summ <= 0:
            return await message.reply('❌ Ошибка. Сумма меньше или равна нулю')
        if summ > user.limitvidach:
            return await message.reply(f'Максимум можете выдать: <code>{to_str(user.limitvidach)}</code>!')

        if len(arg) > 1:
            to_user = User(username=arg[1].replace('@', ''))
        else:
            to_user = User(user=message.reply_to_message.from_user)
        summ2 = to_user.balance + summ

        sql.executescript(f'UPDATE users SET balance = balance + {summ} WHERE id = {to_user.id};\n'
                          f'UPDATE users SET limitvidach =limitvidach - {summ}  WHERE id = {user.id}',
                          True, False)
        return await message.reply(f'Вы успешно выдали пользователю {to_user.link} {to_str(summ)} и его теку'
                                   f'щий баланс: {to_str(summ2)}',
                                   disable_web_page_preview=True)
    except:
        return await message.reply('Какая то ошибка, попробуй заново')


@flags.throttling_key('default')
async def givedonate_handler(message: Message):
    arg = message.text.split()[1:]

    if len(arg) < 1:
        return await message.reply('Используйте: <code>Ддонат {сумма} *{ссылка}</code>')
    try:
        summ = get_cash(arg[0])
        arg[0] = arg[0].replace('$', '')
    except:
        return await message.reply('Используйте: <code>Ддонат {сумма} *{ссылка}</code>')
    if len(arg) > 1 and arg[1].isdigit():
        to_user = User(id=arg[1].replace('@', ''))
    elif len(arg) > 1:
        to_user = User(username=arg[1].replace('@', ''))
    else:
        to_user = User(user=message.reply_to_message.from_user)
    if arg[0][0] == '+':
        summ = to_user.coins + summ
    elif arg[0][0] == '-':
        summ = to_user.coins + summ

    to_user.edit('coins', summ)

    return await message.reply(f'Вы успешно выдали пользователю {to_user.link} {summ} и его теку'
                               f'щий донатный баланс: {to_str(summ)}',
                               disable_web_page_preview=True)


def get_restriction_time(string: str) -> Optional[int]:
    """
    Get user restriction time in seconds

    :param string: string to check for multiplier. The last symbol should be one of:
        "m" for minutes, "h" for hours and "d" for days
    :return: number of seconds to restrict or None if error
    """

    if len(string) < 2:
        return None
    letter = string[-1]
    try:
        number = int(string[:-1])
    except:
        return None
    else:
        if letter == "m" or letter == "м":
            return 60 * number
        elif letter == "h" or letter == "ч":
            return 3600 * number
        elif letter == "d" or letter == "д":
            return 86400 * number
        else:
            return None


@flags.throttling_key('default')
async def privilegia_handler_admin(message: Message):
    arg = message.text.split()[1:]
    if 'vip' in arg[0].lower() or 'вип' in arg[0].lower():
        priva = 1
    elif 'beta' in arg[0].lower() or 'бета' in arg[0].lower():
        priva = 2
    elif 'prem' in arg[0].lower() or 'прем' in arg[0].lower():
        priva = 3
    elif 'elit' in arg[0].lower() or 'элит' in arg[0].lower():
        priva = 4
    elif 'адм' in arg[0].lower() or 'adm' in arg[0].lower():
        priva = 5
    elif '0' in arg[0] or 'игрок' in arg[0].lower():
        priva = None
    elif 'own' in arg[0].lower():
        priva = 6
    else:
        return await message.reply('❌ Такой привилегии не существует!')
    time = None
    try:
        if len(arg) > 3:
            if arg[2] == '-':
                time = get_restriction_time(arg[3])
            user = User(username=arg[1].replace('@', ''))
        elif message.reply_to_message:
            if arg[1] == "-":
                time = get_restriction_time(arg[2])
            user = User(user=message.reply_to_message.from_user)
        else:
            return await message.reply('❌ ФОрмат : [прива] [-\+] *time!')
    except IndexError:
        return await message.reply('❌ ФОрмат : [прива] [-\+] *time!')
    limitvidach: int = 0
    last_vidacha = None
    if priva is not None:
        item = donates[priva]
        if time:
            dt = datetime.now()
            td = timedelta(seconds=time)
            my_date = dt + td
            x = f'{priva},{datetime.now().strftime("%d-%m-%Y %H:%M")},False,{my_date.strftime("%d-%m-%Y %H:%M")}'
        else:
            x = f'{priva},{datetime.now().strftime("%d-%m-%Y %H:%M")},True,None'
        if priva == 4:
            limitvidach = 10_000_000
            last_vidacha = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        if priva == 5:
            limitvidach = 30_000_000
            last_vidacha = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    else:
        item = {'name': 'Игрок', 'price': 0}
        x = None
    user.editmany(donate_source=x, limitvidach=limitvidach, last_vidacha=last_vidacha)

    return await message.reply(f'✅ Вы успешно выдали привилегию <b>{item["name"]}</b> за {item["price"]}🪙 '
                               f'пользователю {user.link}',
                               disable_web_page_preview=True)


@flags.throttling_key('default')
async def other_handler(message: Message):
    other = sql.get_all_data('other')[0]
    kb = InlineKeyboardBuilder()
    kb.add(
        InlineKeyboardButton(text=f"🅱️ Бета-Тест: {'Вкл' if other[6] == 1 else 'Выкл'}", callback_data=f'other_beta'))
    kb.add(InlineKeyboardButton(text=f"✳ Донат2х: {'Вкл' if other[0] == 1 else 'Выкл'}", callback_data=f'other_donate'))
    text = f"✳ Умножения доната : {other[0]}х\n" \
           f"💹 Курс обмена коина: {to_str(other[1])}\n" \
           f"🎁 Макс. размер бонуса: {to_str(other[2])}\n" \
           f"👤 Выдача за рефа: {to_str(other[3])}\n" \
           f"〽 Лимит кредита: {to_str(other[4])}\n" \
           f"❌ Процент кредита: {other[5]}% \n" \
           f"🅱️ Режим Бета-Теста: {'Вкл' if other[6] == 1 else 'Выкл'}"
    return await message.reply(text, reply_markup=kb.adjust(1).as_markup())


@flags.throttling_key('default')
async def other_callhandler(callback: CallbackQuery):
    if callback.from_user.id != owner_id:
        return
    action = callback.data.split('_')[1]
    other = sql.get_all_data('other')[0]
    kb = InlineKeyboardBuilder()
    if action == 'donate':
        sql.execute(f"UPDATE other SET donatex2={2 if other[0] == 1 else 1}", commit=True)
        donatex2 = sql.execute('SELECT donatex2 FROM other', fetch=True)[0][0]
        kb.add(
            InlineKeyboardButton(text=f"🅱️ Бета-Тест: {'Вкл' if other[6] == 1 else 'Выкл'}",
                                 callback_data=f'other_beta'))
        kb.add(
            InlineKeyboardButton(text=f"✳ Донат2х: {'Вкл' if donatex2 == 1 else 'Выкл'}",
                                 callback_data=f'other_donate'))
        text = f"✳ Умножения доната : {donatex2}х\n" \
               f"💹 Курс обмена коина: {to_str(other[1])}\n" \
               f"🎁 Макс. размер бонуса: {to_str(other[2])}\n" \
               f"👤 Выдача за рефа: {to_str(other[3])}\n" \
               f"〽 Лимит кредита: {to_str(other[4])}\n" \
               f"❌ Процент кредита: {other[5]}% \n" \
               f"🅱️ Режим Бета-Теста: {'Вкл' if other[6] == 1 else 'Выкл'}"
        with suppress(TelegramBadRequest):
            await callback.message.delete_reply_markup()
            return await callback.message.edit_text(text, reply_markup=kb.adjust(1).as_markup())
    elif action == 'beta':
        sql.execute(f"UPDATE other SET work={2 if other[6] == 1 else 1}", commit=True)
        work = sql.execute('SELECT work FROM other', fetch=True)[0][0]

        kb.add(
            InlineKeyboardButton(text=f"🅱️ Бета-Тест: {'Вкл' if work == 1 else 'Выкл'}", callback_data=f'other_beta'))
        kb.add(
            InlineKeyboardButton(text=f"✳ Донат2х: {'Вкл' if other[0] == 1 else 'Выкл'}",
                                 callback_data=f'other_donate'))
        text = f"✳ Умножения доната : {other[0]}х\n" \
               f"💹 Курс обмена коина: {to_str(other[1])}\n" \
               f"🎁 Макс. размер бонуса: {to_str(other[2])}\n" \
               f"👤 Выдача за рефа: {to_str(other[3])}\n" \
               f"〽 Лимит кредита: {to_str(other[4])}\n" \
               f"❌ Процент кредита: {other[5]}% \n" \
               f"🅱️ Режим Бета-Теста: {'Вкл' if work == 1 else 'Выкл'}"
        with suppress(TelegramBadRequest):
            await callback.message.delete_reply_markup()
            return await callback.message.edit_text(text, reply_markup=kb.adjust(1).as_markup())


@flags.throttling_key('default')
async def other_kurs_handler(message: Message):
    if message.from_user.id != owner_id:
        return
    arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[0].lower() else message.text.split()[
                                                                                                   2:]
    if len(arg) == 0:
        return await message.reply('❌ Ошибка. Используйте: <code>/kurs (<i>ставка</i>)</code>')
    try:
        summ = get_cash(arg[0])
    except:
        summ = 0
    if summ <= 0:
        return await message.reply('❌ Ошибка.  меньше или равна нулю')
    sql.execute(f"UPDATE other SET coin_kurs={summ}", commit=True)
    return await message.reply(f"💹 Курс обмена коинов: {to_str(summ)}")


@flags.throttling_key('default')
async def other_bonus_handler(message: Message):
    if message.from_user.id != owner_id:
        return
    arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[0].lower() else message.text.split()[
                                                                                                   2:]
    if len(arg) == 0:
        return await message.reply('❌ Ошибка. Используйте: <code>/bonus (<i>ставка</i>)</code>')
    try:
        summ = get_cash(arg[0])
    except:
        summ = 0
    if summ <= 0:
        return await message.reply('❌ Ошибка.  меньше или равна нулю')
    sql.execute(f"UPDATE other SET bonus={summ}", commit=True)
    return await message.reply(f"🎁 Макс. размер бонуса: {to_str(summ)}")


@flags.throttling_key('default')
async def other_zarefa_handler(message: Message):
    if message.from_user.id != owner_id:
        return
    arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[0].lower() else message.text.split()[
                                                                                                   2:]
    if len(arg) == 0:
        return await message.reply('❌ Ошибка. Используйте: <code>/zarefa (<i>ставка</i>)</code>')
    try:
        summ = get_cash(arg[0])
    except:
        summ = 0
    if summ <= 0:
        return await message.reply('❌ Ошибка.  меньше или равна нулю')
    sql.execute(f"UPDATE other SET zarefa={summ}", commit=True)
    return await message.reply(f"👤 Выдача за рефа: {to_str(summ)}")


@flags.throttling_key('default')
async def other_credit_handler(message: Message):
    if message.from_user.id != owner_id:
        return
    arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[0].lower() else message.text.split()[
                                                                                                   2:]
    if len(arg) == 0:
        return await message.reply('❌ Ошибка. Используйте: <code>/credit_limit (<i>ставка</i>)</code>')
    try:
        summ = get_cash(arg[0])
    except:
        summ = 0
    if summ <= 0:
        return await message.reply('❌ Ошибка.  меньше или равна нулю')
    sql.execute(f"UPDATE other SET credit_limit={summ}", commit=True)
    return await message.reply(f"👤 Кредит лимит: {to_str(summ)}")


@flags.throttling_key('default')
async def other_credit_percent_handler(message: Message):
    if message.from_user.id != owner_id:
        return
    arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[0].lower() else message.text.split()[
                                                                                                   2:]
    if len(arg) == 0:
        return await message.reply('❌ Ошибка. Используйте: <code>/credit_percent (<i>ставка</i>)</code>')
    try:
        summ = get_cash(arg[0])
    except:
        summ = 0
    if summ <= 0:
        return await message.reply('❌ Ошибка.  меньше или равна нулю')
    sql.execute(f"UPDATE other SET credit_percent={summ}", commit=True)
    return await message.reply(f"👤 Кредит процент: {to_str(summ)}")


stats_text = 'Ошибочка, ээээээээ!'


async def stats_handler(message: Message):
    ram = psutil.virtual_memory()

    cpu_usage = "<i>" + str(psutil.cpu_count()) + " ядер  " + str(
        psutil.cpu_percent()) + "% с текущим использованием</i>"
    ram_usage = "<i>" + str(ram.used >> 20) + "mb / " + str(ram.total >> 20) + "mb</i>";

    lent = sum([len(all_yaxti()), len(all_vertoleti()),
                len(all_cars()), len(all_businesses()),
                len(all_airplanes()), len(all_moto()), len(all_ferma())])

    text = f'👥 Пользователей в боте: {len(all_users())}\n' \
           f'💭 Чатов добавило бота: {len(all_chats())}\n\n' \
           f'🙉 Промокодов: {len(all_promo())}\n' \
           f'🚫 Забаненых пользователей: {len(all_users_ban())}\n' \
           f'👨‍👩‍👦 Семьи: {len(all_marries())}\n' \
           f'📃 Имущество: <b>{lent}</b>\n➖➖➖➖➖➖\n' \
           f'<b>Версия бота:</b> V1.4.7\n'

    if message.from_user.id == owner_id:
        text += '➖➖➖➖➖➖\n' \
                f'⚙️ CPU usage: {cpu_usage}\n' \
                f'🔩 RAM usage: {ram_usage}\n'
        kb = admin_kb
        if message.chat.id != message.from_user.id:
            kb = InlineKeyboardBuilder()
            kb.add(InlineKeyboardButton(text='💬️ ВДЗУ', callback_data='wdzy'))
            return await message.reply(text, reply_markup=kb.adjust(2).as_markup())
        kb.add(InlineKeyboardButton(text='Инфа о имуществе ➖', callback_data='statsdop'))
        return await message.reply(text, reply_markup=kb.adjust(2).as_markup())
    return await message.reply(text)


async def wdzy_info(call: CallbackQuery):
    chat = Chat_wdz(chat=call.message.chat)
    if chat.source != None:
        status = "Включен" if chat.switch == "on" else "Выключен"
        return await call.message.edit_text(
            f'<b>💬️ ВДЗУ (Выдача денег за участников)</b>\n'
            f'💭 Чат <b>{chat.title}</b> (<code>{chat.id}</code>)\n'
            f'💰 Сумма за 1 чел : <code>{chat.awards}</code>\n'
            f'🌝 Статус - {status}\n'
            f'🔢 Всего добавлено - <b>{chat.count}</b> людей', disable_web_page_preview=True)
    else:
        return await call.message.edit_text(f'💬️ Чат не привязан',
                                            disable_web_page_preview=True)


# async def get_db(call):
#     if call.message.chat.id == call.from_user.id:
#         await call.message.answer_document(document=InputFile('assets/database.db'),
#                                        caption=f'База за {datetime.now()}',)

async def stats_dop_call(call):
    stats_text = f'⛵ Яхты: {len(all_yaxti())}\n' \
                 f'🚁 Вертолёты: {len(all_vertoleti())}\n' \
                 f'🏠 Дома: {len(all_houses())}\n' \
                 f'🏎️ Машины: {len(all_cars())}\n' \
                 f'🧑‍💼 Бизнеса: {len(all_businesses())}\n' \
                 f'✈️ Самолёты: {len(all_airplanes())}\n' \
                 f'🏍️ Мотоциклы: {len(all_moto())}\n' \
                 f'🖥️ Фермы: {len(all_ferma())}\n\n'

    return await call.message.edit_text(stats_text)


async def get_chat_list(call):
    chats = [Chat(source=i) for i in sql.get_all_data('chats')]
    text = f'📃 Список чатов:\n\n'
    for index, chat in enumerate(chats, start=1):
        link = f'@{chat.username}' if chat.username else f'<a href="{chat.invite_link}">Invite*</a>'
        text += f'''{index}. <b>{chat.title}</b> - {link}\n'''
    return await call.message.answer(text)


async def plan_bd(call, state):
    await call.message.answer(text=f'Введите запрос который должен выполниться:',
                              reply_markup=cancel.as_markup())
    await state.set_state(ABD.start)


async def plan_bd_step1(message: Message, state: FSMContext):
    await state.set_state(ABD.step_1)
    await state.update_data(query=message.text)
    return await message.reply('🎄 Введите через сколько выполнить запрос (дата) или "-" если сейчас:',
                               reply_markup=cancel.as_markup())


async def plan_bd_step2(message: Message, state: FSMContext):
    await state.set_state(ABD.step_2)
    await state.update_data(text=message.text)
    return await message.reply('🎄 Введите нужен ли коммит (+ или -):',
                               reply_markup=cancel.as_markup())


async def plan_bd_finish(message: Message, state: FSMContext):
    data = await state.get_data()
    text = data['text']
    query = data['query']
    commit = True if '+' in message.text else False
    await state.clear()

    if text == '-':
        time = 'сейчас'
        seconds = 0
    else:
        now = datetime.now()
        if '.' not in text:
            text = f'{now.day}.{now.month}.{now.year} ' + text
        time = datetime.strptime(text, '%d.%m.%Y %H:%M')
        seconds = (time - now).total_seconds()

    msgs = await message.reply(reply_markup=remove,
                               text=f'🍿 Успешно запланировано на {time}!')

    await asyncio.sleep(seconds)

    with lock:
        sql.execute(query=query, commit=commit, fetch=False)

    return await msgs.reply('🍿 Запрос был успешно выполнен!')
