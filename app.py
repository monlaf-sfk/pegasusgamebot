import re

import time
from contextlib import suppress

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, FSInputFile
from aiogram import Router, F, flags

from handlers.admins.pyrogram import get_user_id

from utils.main.db import sql, timetostr
from config import owner_id
from filters.admin import IsOwner

from keyboard.main import remove
from aiogram.filters import Command

from utils.main.users import User

router = Router()


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
            bot_msg = await message.answer(f'🕘Please wait while me doing SQL request', parse_mode="Markdown")
            if bot_msg:
                with suppress(TelegramBadRequest):
                    return await bot_msg.edit_text(f"{request}")
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
