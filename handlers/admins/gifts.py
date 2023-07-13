import asyncio
from contextlib import suppress

from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery, ReplyKeyboardRemove, BufferedInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

import config
from config import owner_id
from keyboard.main import uchas, cancel
from loader import bot

from utils.items.items import item_case
from utils.main.db import sql
from utils.main.users import User


class Gift(StatesGroup):
    text = State()
    winners = State()
    count_reward = State()
    type_reward = State()
    text_button = State()


class Contest:
    def __init__(self, channel_id: int):
        self.source: tuple = sql.select_data(channel_id, 'channel_id', True, 'contest')
        if self.source is None:
            raise Exception('Not have Contest')
        self.channel_id: int = self.source[0]
        self.participants_count: int = self.source[1]
        self.status: bool = self.source[2]
        self.count_reward: str = self.source[3]
        self.type_reward: str = self.source[4]
        self.winners: str = self.source[5]
        self.text_button: str = self.source[6]

    def edit(self, name, value, attr=True):
        if attr:
            setattr(self, name, value)
        sql.edit_data('channel_id', self.channel_id, name, value, 'contest')
        return value

    @staticmethod
    def create(channel_id, participants_count, status, count_reward, type_reward, winners, text_button):
        res = (channel_id, participants_count, status, count_reward, type_reward, winners, text_button)
        sql.insert_data([res], 'contest')
        return True


class Participants:
    def __init__(self, user_id: int):
        self.source: tuple = sql.select_data(user_id, 'user_id', True, 'participants')
        if self.source is None:
            raise Exception('Not have Participants')
        self.user_id: int = self.source[0]
        self.channel_id: int = self.source[1]

    @staticmethod
    def add_participants(user_id, channel_id):
        res = (user_id, channel_id)
        sql.insert_data([res], 'participants')
        return True


async def gift_handler(message: Message, state: FSMContext):
    if message.from_user.id == owner_id:
        await state.set_state(Gift.text)
        return await message.answer('📃 Пришлите мне сообщение для раздачи:', reply_markup=cancel.as_markup())


async def gift_step1_handler(message: Message, state: FSMContext):
    await state.set_state(Gift.winners)
    await state.update_data(text=message.text)
    return await message.answer('📃 Пришлите количество победителей для раздачи если 0 то всем',
                                reply_markup=cancel.as_markup())


async def gift_step2_handler(message: Message, state: FSMContext):
    try:
        winners = int(message.text)
        if winners <= 0:
            raise ValueError('Number must be a positive integer.')
    except:
        await message.answer('📃 Пришлите количество победителей для раздачи если 0 то всем',
                             reply_markup=cancel.as_markup())
        return state.set_state(Gift.winners)

    await state.set_state(Gift.type_reward)
    await state.update_data(winners=winners)
    return await message.answer('Введите тип награды :\n'
                                "1.Кейсы\n"
                                "2.Донат валюта\n"
                                "3.Валюта\n"
                                "4.Расширение видюх\n"
                                "5.Своя награда "
                                , reply_markup=cancel.as_markup())


async def gift_step3_handler(message: Message, state: FSMContext):
    if message.text.lower() == '1':
        await state.update_data(type_reward='cases')
    elif message.text.lower() == '2':
        await state.update_data(type_reward='coins')
    elif message.text.lower() == '3':
        await state.update_data(type_reward='balance')
    elif message.text.lower() == '4':
        await state.update_data(type_reward='videocards')
    elif message.text.lower() == '5':
        await state.update_data(type_reward='mine')
    else:
        await message.answer('Введите тип награды :\n'
                             "1.Кейсы\n"
                             "2.Донат валюта\n"
                             "3.Валюта\n"
                             "4.Расширение видюх\n"
                             "5.Своя награда ", reply_markup=cancel.as_markup())
        return await state.set_state(Gift.type_reward)
    await state.set_state(Gift.count_reward)
    return await message.answer("📃 Количество награды", reply_markup=cancel.as_markup())


async def gift_step4_handler(message: Message, state: FSMContext):
    try:
        count_reward = int(message.text)
        if count_reward <= 0:
            raise ValueError('Number must be a positive integer.')
    except:
        await state.set_state(Gift.count_reward)
        return await message.answer("📃 Количество награды", reply_markup=cancel.as_markup())

    await state.set_state(Gift.text_button)
    await state.update_data(count_reward=count_reward)
    return await message.answer("Введите текст кнопки", reply_markup=cancel.as_markup())


async def gift_finish_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    try:
        Contest(channel_id=config.channel_offical)
    except:
        Contest.create(config.channel_offical, 0, True, data["count_reward"], data['type_reward'], data['winners'],
                       message.text)
        kb = InlineKeyboardBuilder()
        kb.add(InlineKeyboardButton(text=f'(0){message.text}', callback_data='raz'))
        await bot.send_message(chat_id=config.channel_offical, text=data['text'], reply_markup=kb.as_markup())
        return await message.reply('✅ Розыграш начат!')
    return await message.answer("⁉ Уже идет конкурс ", reply_markup=ReplyKeyboardRemove())


async def gift_participate_handler(callback_query: CallbackQuery):
    try:
        contest = Contest(channel_id=config.channel_offical)
    except:
        contest = None
    if contest.status:
        try:
            participants = Participants(user_id=callback_query.from_user.id)
        except:
            participants = None
        if participants is None:
            user_channel_status = await bot.get_chat_member(chat_id=callback_query.message.chat.id,
                                                            user_id=callback_query.from_user.id)
            if user_channel_status.status == 'left':
                return await callback_query.answer(show_alert=True, text='⁉️ Для начала подпишись на канал !')
            user_chat_status = await bot.get_chat_member(chat_id=config.chat_offical,
                                                         user_id=callback_query.from_user.id)
            if user_chat_status.status == 'left':
                return await callback_query.answer(text='⁉️ Для начала вступи в чат !\n'
                                                        'https://t.me/chat_pegasus', show_alert=True)
            try:
                if User(id=callback_query.from_user.id).blocked:
                    return await callback_query.answer(text='⁉️ Разблокируйте бота в лс !\n\n'
                                                            '⚠ Если он не заблокирован то заблокируйте и разблокируйте бота\n'
                                                            'https://t.me/pegasusgame_bot', show_alert=True)
            except:
                return await callback_query.answer(text='⁉ Зарегистрируйтесь в боте\n\n'
                                                        '⚠ Перейдите в лс боту и нажмите старт\n'
                                                        'https://t.me/pegasusgame_bot', show_alert=True)
            Participants.add_participants(callback_query.from_user.id,
                                          config.channel_offical)
            count = contest.edit('participants_count', contest.participants_count + 1)
            await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id,
                                                message_id=callback_query.message.message_id,
                                                reply_markup=uchas(count, contest.text_button).as_markup())
            await bot.answer_callback_query(callback_query.id, show_alert=True, text='Вы приняли участие в розыгреше ✅')

        else:
            await bot.answer_callback_query(callback_query.id, show_alert=True, text='⁉️ Вы уже участвуете !')
    else:
        await bot.answer_callback_query(callback_query.id, show_alert=True, text='❌ На данный момент нету раздач!')


async def gift_get_handler(message: Message):
    if message.from_user.id != owner_id:
        return
    try:
        contest = Contest(channel_id=config.channel_offical)
    except:
        return await message.reply("❌ Нету запущенных конкурсов")
    if contest.winners == 0:
        participants = sql.get_all_data(table='participants')
    else:
        participants = sql.execute(f'SELECT user_id FROM participants ORDER BY RANDOM() LIMIT {contest.winners};',
                                   fetch=True)
    if contest.type_reward == 'mine':
        text = f'📃 Список победителей:\n\n'
        for index, user in enumerate(participants, start=1):
            text += f'''{index}. {user['user_id']} \n'''
        text_file = BufferedInputFile(bytes(text, 'utf-8'), filename="winners.txt")
        with suppress(TelegramBadRequest):
            await message.reply_document(document=text_file,
                                         caption=f"Список победителей.")

    else:
        users = [user['user_id'] for user in participants]
        send: int = 0
        error: int = 0
        all: int = 0
        for user_id in users:
            user_channel_status = await bot.get_chat_member(chat_id=config.channel_offical, user_id=user_id)
            user_chat_status = await bot.get_chat_member(chat_id=config.chat_offical,
                                                         user_id=user_id)
            blocked = sql.execute(f"SELECT blocked FROM users WHERE id={user_id}", fetchone=True)[0]
            if user_channel_status.status == 'left' or user_chat_status.status == 'left' or blocked:
                continue
            else:
                try:
                    all += 1
                    await asyncio.sleep(1)
                    if contest.type_reward == 'balance':
                        sql.execute(f"UPDATE users SET balance = balance + {contest.count_reward}", commit=True)
                        await bot.send_message(chat_id=user_id,
                                               text="🎁 Вам была выдана награда за участие в розыгрыше!\n"
                                                    f"💵 {contest.count_reward}")
                    elif contest.type_reward == 'cases':
                        sql.execute(
                            "UPDATE users SET cases = jsonb_set(cases, "
                            f"'{{{4}, count}}', "
                            f"to_jsonb((cases->'{4}'->>'count')::int + {contest.count_reward})::text::jsonb) WHERE id={user_id}",
                            commit=True)
                        case = item_case[4]
                        await bot.send_message(chat_id=user_id,
                                               text="🎁 Вам была выдана награда за участие в розыгрыше!\n"
                                                    f"🙃  {case['name']} {case['emoji']} (<code>x{contest.count_reward}</code>)")
                    elif contest.type_reward == 'coins':
                        sql.execute(f"UPDATE users SET coins = coins + {contest.count_reward}", commit=True)
                        await bot.send_message(chat_id=user_id,
                                               text="🎁 Вам была выдана награда за участие в розыгрыше!\n"
                                                    f"🪙 {contest.count_reward}")
                    elif contest.type_reward == 'videocards':
                        sql.execute(f"UPDATE users SET donate_videocards = donate_videocards + {contest.count_reward}",
                                    commit=True)

                        await bot.send_message(chat_id=user_id,
                                               text="🎁 Вам была выдана награда за участие в розыгрыше!\n"
                                                    f"📼 {contest.count_reward}")
                    send += 1
                except:
                    sql.execute(f"UPDATE users SET blocked = True", commit=True)
                    error += 1

        await message.answer(f'Отправлено: {all}\n'
                             f'Успешно: {send}\n'
                             f'Неуспешно: {error}')
    sql.executescript(f'TRUNCATE TABLE participants;\n'
                      f'TRUNCATE TABLE contest;\n', commit=True, fetch=False)
