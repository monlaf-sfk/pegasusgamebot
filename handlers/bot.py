from aiogram import Router
from aiogram.client import bot
from aiogram.types import Message
from aiogram import F

from utils.main.chats import Chat

router = Router()


@router.message(F.new_chat_members)
async def bot_added_to_chat(message: Message):
    if message.chat.type != 'supergroup':
        await message.answer("""
    <b>❌ Ваша группа не является супергруппой❌</b>

    Пожалуйста, превратите вашу группу в супергруппу 
    (просто запретите кому-то отправлять медиафайлы и заново разрешите) 
    и пригласите бота повторно."""
                             , parse_mode='html')
        await bot.leave_chat(message.chat.id)
    else:
        Chat(chat=message.chat)
        return await message.answer("""
    <b>Привет!</b>
    Я игровой бот 💲
    Для того чтобы я мог начать работу, выдай мне пожалуйста права администрации.

    Появились предложения или же вопросы?
    <a href="https://t.me/corching">>Обратись ко мне</a>

    <a href="https://t.me/chat_pegasus">>Так же у нас есть общая беседа </a>
    🗞️ Новости и промокоды: t.me/pegasusdev\n"""

                                    , parse_mode='html')
