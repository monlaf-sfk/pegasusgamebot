import asyncio
import numpy as np
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext

from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from datetime import datetime

from aiogram.utils.keyboard import InlineKeyboardBuilder

from filters.admin import IsOwner
from keyboard.main import cancel, remove
from states.admins import Rass
from utils.main.users import all_users, User
from utils.main.chats import all_chats

router = Router()


@router.callback_query(F.data.startswith("rass_"), IsOwner())
async def rass_menu_handler(call: CallbackQuery, state: FSMContext):
    await state.set_state(Rass.post)
    await state.update_data(action=call.data.split('_')[1])
    return await call.message.answer('📃 Пришлите мне сообщение для рассылки:', reply_markup=cancel.as_markup())


@router.message(Rass.post, IsOwner())
async def rass_step2_handler(message: Message, state: FSMContext):
    await state.update_data(msg=message.text)
    await state.set_state(Rass.kb)
    return await message.answer('🎙️ Клавиатура (name|btn, name|btn\\n) или "-" чтобы пропустить',
                                reply_markup=cancel.as_markup())


@router.message(Rass.kb, IsOwner())
async def rass_step3_handler(message: Message, state: FSMContext):
    if message.text != '-':
        text = message.text.split('\n')
        kb = InlineKeyboardBuilder()
        for i in text:
            i = i.split(',')
            for z in i:
                name, url = z.split('|')
                kb.add(InlineKeyboardButton(text=name, url=url))
                kb.as_markup()
    else:
        kb = None
    await state.update_data(kb=kb)
    await state.set_state(Rass.time)
    return await message.answer('📅 Пришлите мне дату в формате (d.m.Y h:m) или "-" чтобы пропустить',
                                reply_markup=cancel.as_markup())


@router.message(Rass.time, IsOwner())
async def rass_finish_handler(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await state.clear()
    text = message.text
    if text == '-':
        time = 'сейчас'
        seconds = 0
    else:
        now = datetime.now()
        if '.' not in text:
            text = f'{now.day}.{now.month}.{now.year} ' + text
        time = datetime.strptime(text, '%d.%m.%Y %H:%M')
        seconds = (time - now).total_seconds()

    await message.answer(text=f'❤️ Рассылка была запланирована на {time}', reply_markup=remove)

    await asyncio.sleep(seconds)

    part0, part1, part2 = np.array_split(all_users() if data['action'] == 'users' else all_chats(), 3)

    m = await message.answer('Отправлено: 0\n'
                             'Успешно: 0\n'
                             'Неуспешно: 0')

    index = 0
    allow, decline = 0, 0

    msg = data['msg']
    kb = data['kb']
    for user_id in part0:
        index += 1
        try:
            await bot.send_message(chat_id=user_id, text=msg,
                                   reply_markup=kb.as_markup() if kb else None)
            await asyncio.sleep(1)
            allow += 1
        except:
            User(id=user_id).edit('blocked', True)
            decline += 1

    await m.edit_text(f'Отправлено: {index}\n'
                      f'Успешно: {allow}\n'
                      f'Неуспешно: {decline}')

    for user_id in part1:
        index += 1
        try:
            await bot.send_message(chat_id=user_id, text=msg,
                                   reply_markup=kb.as_markup() if kb else None)
            await asyncio.sleep(1)
            allow += 1
        except:
            User(id=user_id).edit('blocked', True)
            decline += 1

    await m.edit_text(f'Отправлено: {index}\n'
                      f'Успешно: {allow}\n'
                      f'Неуспешно: {decline}')

    for user_id in part2:
        index += 1
        try:
            await bot.send_message(chat_id=user_id, text=msg,
                                   reply_markup=kb.as_markup() if kb else None)
            await asyncio.sleep(1)
            allow += 1
        except:
            User(id=user_id).edit('blocked', True)
            decline += 1

    await m.edit_text(f'Отправлено: {index}\n'
                      f'Успешно: {allow}\n'
                      f'Неуспешно: {decline}\n\n'
                      f'Завершено!')
