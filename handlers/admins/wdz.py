from aiogram import Router, F
from aiogram.types import Message
from keyboard.main import check_ls_kb
from utils.main.db import sql
import config
from utils.main.cash import get_cash, to_str
from utils.main.users import User
from utils.main.chat_wdz import Chat_wdz

router = Router()


async def chat_add_handler(message: Message):
    arg = message.text.split()[1:] if not config.bot_name.lower() in message.text.split()[
        0].lower() else message.text.split()[2:]
    if message.chat.id != message.from_user.id:
        if arg[0].lower() == 'бинд':
            chat = Chat_wdz(chat=message.chat)
            if chat.source is None:
                Chat_wdz.create(message.chat)
                return await message.reply(f'💬️ Вы успешно привезали к чату ВДЗУ',
                                           disable_web_page_preview=True)
            else:
                return await message.reply(f'💬️ Чат уже привязан',
                                           disable_web_page_preview=True)
        elif arg[0].lower() == 'анбинд':
            chat = Chat_wdz(chat=message.chat)
            if chat.source != None:
                query = f'DELETE FROM chat_wdz WHERE id={chat.id};'
                sql.execute(query, commit=True, fetch=False)
                return await message.reply(f'💬️ Вы успешно отвезали ВДЗУ',
                                           disable_web_page_preview=True)
            else:
                return await message.reply(f'💬️ Чат не был привязан',
                                           disable_web_page_preview=True)
        elif arg[0].lower() == 'сумма':
            try:
                summ = get_cash(arg[1])
            except:
                return await message.reply(f'💬️ Ошибка : чат сумма (число)')
            chat = Chat_wdz(chat=message.chat)
            if chat.source != None:
                query = f'UPDATE chat_wdz SET awards={summ} WHERE id={chat.id}'
                sql.execute(query, commit=True, fetch=False)
                return await message.reply(f'💬️ Сумма успешно обнавлена в чате на {to_str(summ)}',
                                           disable_web_page_preview=True)
            else:
                return await message.reply(f'💬️ Чат не привязан',
                                           disable_web_page_preview=True)
        elif arg[0].lower() == 'вкл':
            chat = Chat_wdz(chat=message.chat)
            if chat.source != None:
                query = f"UPDATE chat_wdz SET switch='on' WHERE id={chat.id}"
                sql.execute(query, commit=True, fetch=False)
                return await message.reply(f'💬️ ВДЗУ включена',
                                           disable_web_page_preview=True)
            else:
                return await message.reply(f'💬️ Чат не привязан',
                                           disable_web_page_preview=True)
        elif arg[0].lower() == 'выкл':
            chat = Chat_wdz(chat=message.chat)
            if chat.source != None:
                query = f"UPDATE chat_wdz SET switch='off' WHERE id={chat.id}"
                sql.execute(query, commit=True, fetch=False)
                return await message.reply(f'💬️ ВДЗУ выключена',
                                           disable_web_page_preview=True)
            else:
                return await message.reply(f'💬️ Чат не привязан',
                                           disable_web_page_preview=True)

    else:
        return await message.reply(f'💬️ ВДЗУ работает только в группах',
                                   disable_web_page_preview=True)


@router.message(F.new_chat_members)
async def chat_check_handler(message: Message):
    chat = Chat_wdz(chat=message.chat)
    if chat.source is None:
        return
    else:
        if chat.switch == 'on':
            for members in message.new_chat_members:
                if members.is_bot == False:
                    if message.from_user.id != members.id:
                        new_member = sql.select_data(column='reg_date', table='users', title='id', name=members.id,
                                                     row_factor=True)

                        if new_member is None:
                            query = f'SELECT awards FROM chat_wdz WHERE id={chat.id}'
                            summ = sql.execute(query, commit=False, fetch=True)[0][0]
                            user = User(user=message.from_user)
                            user.edit('balance', user.balance + summ)
                            query = f'UPDATE chat_wdz SET count= count+1 WHERE id={chat.id}'
                            sql.execute(query, commit=True, fetch=False)
                            await message.reply(
                                f'💬️ <a href="tg://user?id={members.id}">{members.first_name.replace("<", "").replace(">", "")}</a> Добро пожаловать в чат Pegasus!'
                                f'\n⏩ Перейди в лс для получения полного доступа в боте!',
                                reply_markup=check_ls_kb.as_markup())
                        else:
                            await message.reply(
                                f'💬️ <a href="tg://user?id={members.id}">{members.first_name.replace("<", "").replace(">", "")}</a> Добро пожаловать в чат Pegasus!')
                    else:

                        await message.reply(
                            f'💬️ <a href="tg://user?id={members.id}">{members.first_name.replace("<", "").replace(">", "")}</a> Добро пожаловать в чат Pegasus!')
