from aiogram import Router, F, flags
from aiogram.filters import Command
from aiogram.types import Message

from filters.admin import IsOwner
from handlers.admins.main import get_restriction_time
from loader import bot
from utils.main.users import User

router = Router()


@router.message(Command(commands=['чс', 'анчс']), IsOwner())
@flags.throttling_key('default')
async def ban_user_handler(message: Message):
    arg = message.text.split()
    if arg[0].lower() == '/чс':
        arg = arg[1:]
        is_always = False
        reason = ''
        if (len(arg) > 1 and not message.reply_to_message) or (
                len(arg) >= 1 and message.reply_to_message):  # !mute with arg
            restriction_time = get_restriction_time(arg[1] if not message.reply_to_message else arg[0])
            if restriction_time:
                if (len(arg) >= 2 and message.reply_to_message) or (len(arg) >= 3 and not message.reply_to_message):
                    reason = f'\n{" ".join(map(str, arg[2:])) if not message.reply_to_message else " ".join(map(str, arg[1:]))}'
            else:
                if (len(arg) >= 1 and message.reply_to_message) or (len(arg) >= 2 and not message.reply_to_message):
                    reason = f'\n{" ".join(map(str, arg[1:])) if not message.reply_to_message else " ".join(map(str, arg[:]))}'
                restriction_time = None
                is_always = True
        else:
            if (len(arg) >= 1 and message.reply_to_message) or (len(arg) >= 2 and not message.reply_to_message):
                reason = f'\n{" ".join(map(str, arg[1:])) if not message.reply_to_message else " ".join(map(str, arg[:]))}'
            restriction_time = None
            is_always = True
        admin = User(user=message.from_user)

        if message.reply_to_message:
            await User(user=message.reply_to_message.from_user).banf(reason, admin, bot=bot, time=restriction_time,
                                                                     is_always=is_always)
        elif len(arg) >= 1 and arg[0].isdigit():
            await User(id=arg[0]).banf(reason, admin, bot=bot, time=restriction_time, is_always=is_always)
        elif len(arg) >= 1:
            await User(username=arg[0].lower().replace('@', '')).banf(reason, admin, bot=bot, time=restriction_time,
                                                                      is_always=is_always)

        else:
            return await message.reply('📖 Формат ввода : /mute [user] [время] [причина]'
                                       '\n ⚠ Примечание: если не указать время бан/мут выдается навсегда!')

        return await message.reply('🟢 Пользователь забанен')
    else:
        arg = arg[1:]
        if message.reply_to_message:
            User(user=message.reply_to_message.from_user).edit('ban_source', None)
        elif len(arg) >= 1 and arg[0].isdigit():
            User(id=arg[0]).edit('ban_source', None)
        elif len(arg) >= 1:
            User(username=arg[0].lower().replace('@', '')).edit('ban_source', None)
        else:
            return await message.reply('⛔ Неверный формат команды')
        return await message.reply('🔓 Пользователь разбанен')


@router.message(Command(commands=['nickban', 'unnickban', 'анникбан', 'никбан']), IsOwner())
@flags.throttling_key('default')
async def nickban_user_handler(message: Message):
    arg = message.text.split()
    if arg[0].lower() in ['/nickban', '/никбан']:
        arg = arg[1:]
        if message.reply_to_message:
            User(user=message.reply_to_message.from_user).edit('nickban', True)
        elif len(arg) >= 1 and arg[0].isdigit():
            User(id=arg[0]).edit('nickban', True)
        elif len(arg) >= 1:
            User(username=arg[0].lower().replace('@', '')).edit('nickban', True)
        else:
            return await message.reply('⛔ Неверный формат команды')
        return await message.reply('🟢 Пользователю был закрыт доступ к смене ника!')
    else:
        arg = arg[1:]
        if message.reply_to_message:
            User(user=message.reply_to_message.from_user).edit('nickban', False)
        elif len(arg) >= 1 and arg[0].isdigit():
            User(id=arg[0]).edit('nickban', False)
        elif len(arg) >= 1:
            User(username=arg[0].lower().replace('@', '')).edit('nickban', False)
        else:
            return await message.reply('⛔ Неверный формат команды')
        return await message.reply('🔓 Пользователю был открыт доступ к смене ника!')


@router.message(Command(commands=['payban', 'unpayban']), IsOwner())
@flags.throttling_key('default')
async def payban_user_handler(message: Message):
    arg = message.text.split()
    if arg[0].lower() in ['/payban']:
        arg = arg[1:]
        if message.reply_to_message:
            User(user=message.reply_to_message.from_user).edit('payban', True)
        elif len(arg) >= 1 and arg[0].isdigit():
            User(id=arg[0]).edit('payban', True)
        elif len(arg) >= 1:
            User(username=arg[0].lower().replace('@', '')).edit('payban', True)
        else:
            return await message.reply('⛔ Неверный формат команды')
        return await message.reply('🟢 Пользователю был закрыт доступ к переводам!')
    else:
        arg = arg[1:]
        if message.reply_to_message:
            User(user=message.reply_to_message.from_user).edit('payban', False)
        elif len(arg) >= 1 and arg[0].isdigit():
            User(id=arg[0]).edit('payban', False)
        elif len(arg) >= 1:
            User(username=arg[0].lower().replace('@', '')).edit('payban', False)
        else:
            return await message.reply('⛔ Неверный формат команды')
        return await message.reply('🔓 Пользователю был открыт доступ к переводам!')
