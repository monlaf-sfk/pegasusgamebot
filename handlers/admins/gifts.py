import asyncio

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
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
    summ = State()
    type = State()


async def gift_handler(message: Message, state: FSMContext):
    if message.from_user.id == owner_id:
        await state.set_state(Gift.text)
        return await message.answer('📃 Пришлите мне сообщение для раздачи:', reply_markup=cancel.as_markup())


async def gift_step1_handler(message, state: FSMContext):
    await state.set_state(Gift.summ)
    await state.update_data(text=message.text)
    return await message.answer('📃 Пришлите мне сумму для раздачи:', reply_markup=cancel.as_markup())


async def gift_step2_handler(message, state: FSMContext):
    await state.set_state(Gift.type)
    await state.update_data(summ=message.text)
    return await message.answer('Введи валюту 1 Доллары 2 Кейсы 3 Донат ', reply_markup=cancel.as_markup())


async def gift_finish_handler(message, state: FSMContext):
    try:
        data = await state.get_data()
        await state.clear()
        kb = InlineKeyboardBuilder()
        kb.add(InlineKeyboardButton(text=f'(0)✅Участвовать', callback_data='raz'))
        text = data['text']
        summ = data['summ']
        type = message.text
        sql.executescript(f'UPDATE other SET summa={summ};\n'
                          f"UPDATE other SET type_gift='{type}';\n"
                          f"UPDATE other SET switch='on';\n", commit=True, fetch=False)
        await bot.send_message(chat_id=config.channel_offical, text=text, reply_markup=kb.as_markup())
        await bot.send_message(chat_id=message.from_user.id, text='✅ Розыграш начат!')
    except Exception as e:
        print(e)


async def gift_participate_handler(callback_query: CallbackQuery):
    switch = sql.get_only_data(column='switch', table='other')[0]
    if switch == 'on':
        member = sql.select_data(column='user_id', table='gift_users', title='user_id',
                                 name=callback_query.from_user.id, row_factor=True)
        if member is None:
            user_channel_status = await bot.get_chat_member(chat_id=config.channel_offical,
                                                            user_id=callback_query.from_user.id)
            if user_channel_status.status == 'left':
                return await callback_query.answer(show_alert=True, text='⁉️ Для начала подпишись на канал !')
            user_chat_status = await bot.get_chat_member(chat_id=config.chat_offical,
                                                         user_id=callback_query.from_user.id)
            if user_chat_status.status == 'left':
                return await callback_query.answer(text='⁉️ Для начала вступи в чат !\n'
                                                        'https://t.me/chat_pegasus', show_alert=True)
            if User(id=callback_query.from_user.id).blocked:
                return await callback_query.answer(text='⁉️ Разблокируйте бота в лс !\n'
                                                        'https://t.me/pegasusgame_bot', show_alert=True)
            res = (callback_query.from_user.id,)
            sql.insert_data([res], 'gift_users')
            sql.execute("UPDATE other SET count=count+1", commit=True, fetch=False)
            count = sql.get_only_data(column='count', table='other')[0]
            await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id,
                                                message_id=callback_query.message.message_id,
                                                reply_markup=uchas(count).as_markup())
            await bot.answer_callback_query(callback_query.id, show_alert=True, text='Вы приняли участие в розыгреше ✅')

        else:
            await bot.answer_callback_query(callback_query.id, show_alert=True, text='⁉️ Вы уже участвуете !')
    else:
        await bot.answer_callback_query(callback_query.id, show_alert=True, text='❌ На данный момент нету раздач!')


async def gift_get_handler(message: Message):
    if message.from_user.id == owner_id:
        row = sql.get_all_data(table='gift_users')
        users = [user[0] for user in row]
        send: int = 0
        error: int = 0
        all: int = 0
        for id in users:
            user_channel_status = await bot.get_chat_member(chat_id=config.channel_offical, user_id=id)
            user_chat_status = await bot.get_chat_member(chat_id=config.chat_offical,
                                                         user_id=id)
            user = User(id=id)
            if user_channel_status.status == 'left' or user_chat_status.status == 'left' or user.blocked:
                pass
            else:
                try:
                    all += 1
                    balik = sql.get_only_data(column='summa', table='other')[0]
                    await asyncio.sleep(1)
                    type = sql.get_only_data(column='type_gift', table='other')[0]
                    if type == 1:
                        user.edit('balance', user.balance + balik)
                        await bot.send_message(chat_id=id, text="🎁 Вам была выдана награда за участие в розыгрыше!\n"
                                                                f"💵 {balik}")
                    if type == 2:
                        user.cases = list(user.cases)
                        user.set_case(item_id=4, x=balik)
                        case = item_case[4]
                        await bot.send_message(chat_id=id, text="🎁 Вам была выдана награда за участие в розыгрыше!\n"
                                                                f"🙃  {case['name']} {case['emoji']} (<code>x{balik}</code>)")
                    if type == 3:
                        user.edit('coins', user.coins + balik)
                        await bot.send_message(chat_id=id, text="🎁 Вам была выдана награда за участие в розыгрыше!\n"
                                                                f"🪙 {balik}")
                    send += 1
                except:
                    user.edit('blocked', True)
                    error += 1
                    pass
        await message.answer(f'Отправлено: {all}\n'
                             f'Успешно: {send}\n'
                             f'Неуспешно: {error}')
        sql.executescript(f'TRUNCATE TABLE gift_users;\n'
                          f"UPDATE other SET switch='off';"
                          f"UPDATE other SET count=0;", commit=True, fetch=False)
    else:
        await message.answer('Вы не являетесь создателем бота!')
