import itertools
from contextlib import suppress

import aiohttp
from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from config import bot_name
from filters.triggers import Trigger
from utils.main.cash import to_str
from utils.main.users import User
from fuzzywuzzy import fuzz

router = Router()
rewards_dict = {
    range(0, 50): ("Начинающий", 17580),
    range(50, 100): ("Усердный", 17580),
    range(100, 150): ("Загадочный", 17580),
    range(150, 200): ("Талантливый", 17580),
    range(200, 250): ("Опытный", 17580),
    range(300, 350): ("Мастер", 17580),
    range(400, 450): ("Гений", 17580),
    range(500, 550): ("Магистр", 17580),
    range(600, 650): ("Профессор", 17580),
    itertools.count(650): ("Мудрейший", 17580)
}

min_similarity_threshold = 85


class PuzzleCallbackFactory(CallbackData, prefix="puzzle"):
    action: str


def puzzle_kb(new=False):
    keyboard = InlineKeyboardBuilder()
    if not new:
        keyboard.add(
            InlineKeyboardButton(text="❓ Повторить загадку",
                                 callback_data=PuzzleCallbackFactory(action='repeat').pack()))
        keyboard.add(
            InlineKeyboardButton(text="✉ Узнать ответ ", callback_data=PuzzleCallbackFactory(action='answer').pack()))

    else:
        keyboard.add(
            InlineKeyboardButton(text="❓ Новая загадка",
                                 callback_data=PuzzleCallbackFactory(action='new').pack()))

    return keyboard.as_markup()


class Puzzles(StatesGroup):
    waiting_answer = State()


async def get_quiz():
    ua = UserAgent()
    user_agent = ua.random
    headers = {
        'User-Agent': user_agent
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get('https://zagadki-otvetami.ru/sluchajnaya-zagadka/') as response:
            body = await response.text()
            soup = BeautifulSoup(body, "lxml")
            # Ищем блок с загадкой и ответом
            riddle_text = soup.find('div', class_='text').get_text()

            # Extract the correct answer
            answer = soup.find('input', class_='inp_otvet')['value']

            if riddle_text:
                riddle_text = riddle_text.replace('&quot;', '"').replace('<br>', '\n').strip()
                riddle_text = riddle_text.split('\n')
                formatted_qiuz_text = '| ' + '\n| '.join(riddle_text)
            return formatted_qiuz_text, answer
    return None


@router.message(Trigger(["загадка"]))
async def quiz_handler(message: Message, state: FSMContext):
    user = User(user=message.from_user)
    old_state = await state.get_state()
    prefix, reward = next((reward for rng, reward in rewards_dict.items() if user.quiz_answers in rng), None)
    kb = puzzle_kb()
    if message.chat.type != 'private':
        kb = None
    if old_state == 'Puzzles:waiting_answer':
        data = await state.get_data()
        with suppress(TelegramBadRequest):
            await message.reply(f'[{prefix}] {user.link}, загадка уже загадана:\n'
                                f'{data["quiz"]}\n\n'
                                f'🔎 Подсказка: {len(data["answer"])} буквы',
                                disable_web_page_preview=True, reply_markup=kb)
        return
    quiz = await get_quiz()
    if quiz:

        qiuz_text, answer = quiz
        await state.set_data(data={'answer': answer.lower(), 'quiz': qiuz_text})
        await state.set_state(Puzzles.waiting_answer)

        await message.reply(
            f'[{prefix}] {user.link}:\n{qiuz_text}\n\n🔎 Подсказка: {len(answer)} буквы\n\n➡️ Для ответа введите «Ответ [ответ]»',
            reply_markup=kb,
            disable_web_page_preview=True)
    else:
        await message.reply(f'{user.link}, извините, не удалось получить. Попробуйте позже.',
                            disable_web_page_preview=True)


@router.message(Trigger(['сдаюсь']), Puzzles.waiting_answer)
async def quiz_giveup_handler(message: Message, state: FSMContext):
    user = User(user=message.from_user)
    data = await state.get_data()
    prefix, reward = next((reward for rng, reward in rewards_dict.items() if user.quiz_answers in rng), None)

    await state.set_state(None)
    if message.chat.type != 'private':
        await message.reply(f'[{prefix}] {user.link}, ответ на загадку: «{data["answer"]}» 😒',
                            disable_web_page_preview=True)
    else:
        await message.reply(f'[{prefix}] {user.link}, ответ на загадку: «{data["answer"]}» 😒',
                            disable_web_page_preview=True, reply_markup=puzzle_kb(True))


@router.message(Trigger(['ответ']), Puzzles.waiting_answer)
async def quiz_answer_handler(message: Message, state: FSMContext):
    user = User(user=message.from_user)
    data = await state.get_data()
    arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[
        0].lower() else message.text.split()[2:]
    kb = puzzle_kb()
    if message.chat.type != 'private':
        kb = None
    prefix, reward = next((reward for rng, reward in rewards_dict.items() if user.quiz_answers in rng), None)

    if len(arg) == 0:
        return await message.reply(f'[{prefix}] {user.link}, введите «Ответ [ответ на загадку]»',
                                   disable_web_page_preview=True, reply_markup=kb)
    arg = " ".join(arg)

    similarity = fuzz.ratio(arg, data["answer"])

    if similarity >= min_similarity_threshold:
        await state.set_state(None)
        user.editmany(balance=user.balance + reward, quiz_answers=user.quiz_answers + 1)
        await message.reply(f'[{prefix}] {user.link}, правильно! Это слово «{data["answer"]}»!\n'
                            f'💸 Приз: {to_str(reward)}!\n'
                            f'💰 Баланс: {to_str(user.balance)} \n',
                            disable_web_page_preview=True, reply_markup=kb)
    else:
        await message.reply(f'[{prefix}] {user.link}, неправильно, попробуй еще 😣',
                            disable_web_page_preview=True, reply_markup=kb)


@router.message(Puzzles.waiting_answer, F.chat.type.in_({"private"}))
async def quiz_answer_handler(message: Message, state: FSMContext):
    user = User(user=message.from_user)
    data = await state.get_data()
    similarity = fuzz.ratio(message.text.lower(), data["answer"])
    prefix, reward = next((reward for rng, reward in rewards_dict.items() if user.quiz_answers in rng), None)
    if similarity >= min_similarity_threshold:
        await state.set_state(None)
        user.editmany(balance=user.balance + reward, quiz_answers=user.quiz_answers + 1)
        await message.reply(f'[{prefix}] {user.link}, правильно! Это слово «{data["answer"]}»! \n'
                            f'💸 Приз: {to_str(reward)}!\n'
                            f'💰 Баланс: {to_str(user.balance)} \n',
                            disable_web_page_preview=True, reply_markup=puzzle_kb(True))
    else:
        await message.reply(f'[{prefix}] {user.link}, неправильно, попробуй еще 😣',
                            disable_web_page_preview=True, reply_markup=puzzle_kb())


@router.callback_query(PuzzleCallbackFactory.filter())
async def quiz_call_handler(callback: CallbackQuery, state: FSMContext, callback_data: PuzzleCallbackFactory):
    user = User(id=callback.from_user.id)
    data = await state.get_data()
    prefix, reward = next((reward for rng, reward in rewards_dict.items() if user.quiz_answers in rng), None)

    if callback_data.action == 'repeat':
        with suppress(TelegramBadRequest):
            await callback.message.edit_text(f'[{prefix}] {user.link}, загадка уже загадана:\n'
                                             f'{data["quiz"]}\n\n'
                                             f'🔎 Подсказка: {len(data["answer"])} буквы',
                                             disable_web_page_preview=True, reply_markup=puzzle_kb())
    elif callback_data.action == 'answer':
        await state.set_state(None)
        with suppress(TelegramBadRequest):
            await callback.message.edit_text(f'[{prefix}] {user.link}, ответ на загадку: «{data["answer"]}» 😒',
                                             disable_web_page_preview=True, reply_markup=puzzle_kb(True))
    elif callback_data.action == 'new':
        quiz = await get_quiz()
        if quiz:
            qiuz_text, answer = quiz
            await state.set_data(data={'answer': answer.lower(), 'quiz': qiuz_text})
            await state.set_state(Puzzles.waiting_answer)
            with suppress(TelegramBadRequest):
                await callback.message.edit_text(
                    f'[{prefix}] {user.link}:\n{qiuz_text}\n\n🔎 Подсказка: {len(answer)} буквы\n\n➡️ Для ответа введите «Ответ [ответ]»',
                    reply_markup=puzzle_kb(),
                    disable_web_page_preview=True)
        else:
            with suppress(TelegramBadRequest):
                await callback.message.edit_text(
                    f'[{prefix}] {user.link}, извините, не удалось получить. Попробуйте позже.',
                    disable_web_page_preview=True)
