import io
import re

import time
from contextlib import suppress

import aiohttp
import pandas as pd
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, FSInputFile, BufferedInputFile
from aiogram import Router, F, flags
from matplotlib import pyplot as plt
from scipy.signal import savgol_filter

from filters.triggers import Trigger
from handlers.admins.pyrogram import get_user_id
from utils.main.bitcoin import to_usd
from utils.main.cash import to_str

from utils.main.db import sql, timetostr
from config import owner_id
from filters.admin import IsOwner

from keyboard.main import remove
from aiogram.filters import Command

from utils.main.euro import uah_to_usd, euro_to_usd
from utils.main.users import User

from fake_useragent import UserAgent

router = Router()


async def get_anek():
    ua = UserAgent()
    user_agent = ua.random
    headers = {
        'User-Agent': user_agent
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get('https://www.anekdot.ru/random/anekdot/') as response:
            body = await response.text()
            res = re.search(r'<div class="text">([^<]+)</div>', body, re.IGNORECASE)
            if res:
                anek = res.group(1).replace('&quot;', '"').replace('<br>', '\n').strip()
                return anek
            return None


@router.message(Trigger(["анекдот"]))
async def send_anek(message: Message):
    anek = await get_anek()
    user = User(user=message.from_user)
    if anek:

        await message.reply(f'{user.link}, анекдот:\n{anek}', disable_web_page_preview=True)
    else:
        await message.reply(f'{user.link}, извините, не удалось получить анекдот. Попробуйте позже.',
                            disable_web_page_preview=True)


def uah_btc_euro_iad():
    data_uah = pd.read_csv('assets/uah.price', sep=' ', header=None, names=['Date', 'Time', 'UAH_Price'])
    data_btc = pd.read_csv('assets/btc.price', sep=' ', header=None, names=['Date', 'Time', 'BTC_Price'])
    data_euro = pd.read_csv('assets/euro.price', sep=' ', header=None, names=['Date', 'Time', 'Euro_Price'])

    # Преобразование столбцов в нужные форматы
    for data in [data_uah, data_btc, data_euro]:
        data['Date'] = pd.to_datetime(data['Date'], format='%Y-%m-%d')
        data['Time'] = pd.to_datetime(data['Time'], format='%H:%M:%S').dt.time

        # Создание столбца 'Date' для временных меток
        data['Date'] = pd.to_datetime(data['Date'].astype(str) + ' ' + data['Time'].astype(str))

    end_date = data_uah['Date'].max()
    start_date = end_date - pd.DateOffset(days=5)

    filtered_data_uah = data_uah[(data_uah['Date'] >= start_date) & (data_uah['Date'] <= end_date)]
    filtered_data_btc = data_btc[(data_btc['Date'] >= start_date) & (data_btc['Date'] <= end_date)]
    filtered_data_euro = data_euro[(data_euro['Date'] >= start_date) & (data_euro['Date'] <= end_date)]

    # Применение скользящего среднего для сглаживания данных
    window_size = 5  # Размер окна для скользящего среднего
    poly_order = 2  # Порядок полинома для скользящего среднего

    smoothed_uah = savgol_filter(filtered_data_uah['UAH_Price'], window_size, poly_order)
    smoothed_btc = savgol_filter(filtered_data_btc['BTC_Price'], window_size, poly_order)
    smoothed_euro = savgol_filter(filtered_data_euro['Euro_Price'], window_size, poly_order)

    # Создание графика
    dark_gray = '#333333'  # Dark gray background color
    plt.figure(figsize=(16, 11), facecolor=dark_gray, dpi=80)

    # Plot smoothed UAH data
    plt.plot(filtered_data_uah['Date'], smoothed_uah, marker='', linestyle='-', color='b',
             label='Сглаженная динамика цен на UAH')

    # Plot smoothed Bitcoin data
    plt.plot(filtered_data_btc['Date'], smoothed_btc, marker='', linestyle='-', color='g',
             label='Сглаженная динамика цен на BTC')

    # Plot smoothed Euro data
    plt.plot(filtered_data_euro['Date'], smoothed_euro, marker='', linestyle='-', color='r',
             label='Сглаженная динамика цен на Euro')
    # Сохранение и возвращение изображения
    img_byte_array = io.BytesIO()
    plt.xlabel('Дата', color='white', fontsize=25)
    plt.ylabel('Цена', color='white', fontsize=25)
    plt.title('Изменения цен', color='white', fontsize=30)
    plt.xticks(rotation=45, color='white', fontsize=12)
    plt.yticks(color='white', fontsize=12)
    plt.legend()
    plt.grid(True, color=dark_gray, linestyle='--', linewidth=0.5, alpha=0.7)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.savefig(img_byte_array, format='png')
    img_byte_array.seek(0)
    return img_byte_array


@router.message(Trigger(["Курс"]))
async def send_anek(message: Message):
    user = User(id=message.from_user.id)
    img = uah_btc_euro_iad()
    text_file = BufferedInputFile(img.getvalue(), filename="fetch.png")
    return await message.reply_photo(caption=f'{user.link}, курс валют на данный момент:\n'
                                             f'💷 Юань: {to_str(uah_to_usd(1))}\n'
                                             f'💶 Евро: {to_str(euro_to_usd(1))}\n'
                                             f'🧀 BTC: {to_str(to_usd(1))}\n'

                                     , photo=text_file)


@router.message(F.photo)
@flags.throttling_key('default')
async def cmd_message_from_bot(message: Message):
    if message.from_user.id == owner_id and message.chat.type == 'private':
        await message.reply(message.photo[-1].file_id)


@router.message(F.text.startswith('.ид'))
@flags.throttling_key('default')
async def cmd_message_from_bot(message: Message):
    if not message.reply_to_message:

        if len(message.text.split()[1:]) == 0:
            return await message.reply(
                f'ID: {"@" + message.from_user.username if message.from_user.username else message.from_user.full_name} — <code>{message.from_user.id}</code> \n'
                f'CHAT ID: {message.chat.title} — <code>{message.chat.id}</code>')
        id = await get_user_id(message.text.split()[1:])

        return await message.reply(f'ID: {message.text.split()[1:][0]} — <code>{id}</code> \n'
                                   f'CHAT ID: {message.chat.title} — <code>{message.chat.id}</code>')
    if message.reply_to_message:
        return await message.reply(
            f'ID: {"@" + message.reply_to_message.from_user.username if message.reply_to_message.from_user.username else message.reply_to_message.from_user.full_name} — <code>{message.reply_to_message.from_user.id}</code> '
            f'\nCHAT ID: {message.reply_to_message.chat.title} — <code>{message.reply_to_message.chat.id}</code>')


def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def multiply(a, b):
    return a * b


def divide(a, b):
    return a / b


operations = {
    "+": add,
    "-": subtract,
    "*": multiply,
    "/": divide
}


def to_rpn(expression):
    # Разбивка выражения на операнды и операции, а также скобки
    pattern = r"(\d+(?:\.\d+)?)|\s*([+\-*/^]|sqrt|[()])\s*"
    tokens = re.findall(pattern, expression)
    # Список для хранения выходной последовательности
    output = []
    # Стек для хранения операций
    opstack = []
    # Словарь с приоритетами операций
    priority = {
        "+": 1,
        "-": 1,
        "*": 2,
        "/": 2
    }
    for token in tokens:
        if token[0]:
            output.append(float(token[0]))
        elif token[1] == "(":
            opstack.append(token[1])
        elif token[1] == ")":
            while opstack and opstack[-1] != "(":
                output.append(opstack.pop())
            opstack.pop()  # Удаляем открывающую скобку из стека
        else:
            while opstack and priority.get(token[1], 0) <= priority.get(opstack[-1], 0):
                output.append(opstack.pop())
            opstack.append(token[1])
    while opstack:
        output.append(opstack.pop())
    return output


# Функция для вычисления выражения в обратной польской записи
def calculate_rpn(expression):
    # Стек для хранения операндов
    stack = []
    for token in expression:
        if isinstance(token, float):
            stack.append(token)
        else:
            b = stack.pop()
            a = stack.pop()
            stack.append(operations[token](a, b))
    return stack[0]


@flags.throttling_key('default')
async def calc_handler(message):
    with suppress(ValueError):
        try:
            operands = str(message.text.split()[1:][0])

            text2 = '<b>📟 Решение: </b>\n'
            rpn = to_rpn(operands)
            result = calculate_rpn(rpn)
            text2 += f'{result}'
            return await message.reply(text2)
        except ZeroDivisionError:
            return await message.reply('❌ На ноль делить нельзя!')
        except IndexError:
            return await message.reply('❌ Проверьти правильность ввода примера!')

    return await message.reply('❌ Проверьти правильность ввода!\n'
                               'Пример: реши 1 + 1')


async def forward_from(message):
    return


@router.message(F.text == "❌")
async def cancel_handler(m, state):
    await state.clear()
    return await m.reply(text="Отменено.", reply_markup=remove)


@flags.throttling_key('default')
async def sql_handler(message):
    if message.from_user.id == owner_id:
        try:
            query = message.text[message.text.find(' '):]
            request = sql.executescriptSql(query, True, False)
            bot_msg = await message.answer(f'🕘Please wait while me doing SQL request', parse_mode="Markdown")
            if bot_msg:
                await bot_msg.edit_text(f"🚀SQL Запрос был выполнен\n"
                                        f"{request}")
        except Exception as e:
            await message.answer(f"❌ Возникла ошибка при изменении\n⚠️ Ошибка: {e}")
    else:
        await message.answer("❌ *Эта команда доступна только создателю бота*", parse_mode="Markdown")


@router.message(Command("fetch"), IsOwner())
@flags.throttling_key('default')
async def fetch_handler(message):
    if message.from_user.id == owner_id:
        try:
            query = message.text[message.text.find(' '):]
            request = sql.executescriptSql(query, False, True)
            file = f'SQL: {request}\n'

            for index, i in enumerate(request, start=1):
                file += f'{index}. {i}\n'
            text_file = BufferedInputFile(bytes(file, 'utf-8'), filename="fetch.txt")
            with suppress(TelegramBadRequest):
                await message.reply_document(document=text_file,
                                             caption=f"Запрос {query}.")
        except Exception as e:
            await message.answer(f"❌ Возникла ошибка при изменении\n⚠️ Ошибка: {e}")
    else:
        await message.answer("❌ *Эта команда доступна только создателю бота*", parse_mode="Markdown")


from datetime import datetime


@router.message(Command("logs"), IsOwner())
@flags.throttling_key('default')
async def logs_handler(message: Message):
    with suppress(TypeError):
        return await message.reply_document(
            document=FSInputFile(f'assets/logs/{datetime.now().strftime("%d.%m.%y")}.log')
        )

    return await message.reply("Не удалось отправить логи.")


@flags.throttling_key('default')
async def ban_handler(message: Message):
    if message.chat.id == message.from_user.id:
        user = User(id=message.from_user.id)
        return await message.reply(
            text=f'<i>🚫 {user.link}, ваш игровой аккаунт был заблокирован за Нарушение игровых правил Pegasus бота.</i>\n\n'
                 f'📛 Причина: <b>{user.ban.reason}</b>\n'
                 f'⏱ Время до разбана {"Навсегда" if user.ban.is_always else timetostr((user.ban.to_date - datetime.now()).total_seconds())}'
            , disable_web_page_preview=True)


@router.message(Command("ping"), IsOwner())
@flags.throttling_key('default')
async def ping_handler(message: Message):
    if message.forward_date != None:
        return
    a = time.time()
    bot_msg = await message.answer(f'🕘Please wait while me doing request', parse_mode="Markdown")
    if bot_msg:
        b = time.time()
        await bot_msg.edit_text(f'🚀 Пинг: *{round((b - a) * 1000)} ms*', parse_mode="Markdown")
