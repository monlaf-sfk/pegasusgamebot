from __future__ import annotations

import time

from aiogram.filters import BaseFilter
from aiogram.types import Message

from config import bot_name, owner_id
from loader import bot
from utils.main.db import sql

last_use3 = {}


async def all_handler(message: Message):
    try:
        if last_use3.get(message.from_user.id):
            if time.time() - last_use3[message.from_user.id] < 10000:
                return
        last_use3[message.from_user.id] = time.time()
        if sql.execute("SELECT work FROM other", commit=False, fetch=True)[0][0] != 1:
            return
        return await bot.send_message(message.chat.id, "⛔ Технические Работы !\n"
                                                       "Бот вернеться в скором времени.")
    except Exception as e:
        print(e)


class Trigger(BaseFilter):
    def __init__(self, trigger: str | list, args: bool = False):
        self.trigger = trigger.lower() if type(trigger) == str else [i.lower() for i in trigger]
        self.args = args

        BaseFilter.__init__(self)

    async def __call__(self, message: Message) -> bool:
        try:
            if message.from_user.is_bot == True:
                return False
            if message.reply_to_message:
                if message.reply_to_message.from_user.is_bot == True:
                    return False
            args = message.text.split()

            if args[0].lower() in [f'@{bot_name}', f'{bot_name}']:
                args = args[1:]
            if len(args) == 0:
                return False
            one = ' '.join(args).replace(f'{bot_name}', '').replace('!', '').replace('.', ''). \
                replace('/', '').replace('@', '').lower()

            one = one.startswith(self.trigger) if type(self.trigger) == str else one.split()[
                                                                                     0] in self.trigger or one in self.trigger

            try:
                two = args[1] if self.args else True
            except:
                two = False
            if message.from_user.id != owner_id and one:
                if sql.execute("SELECT work FROM other", commit=False, fetch=True)[0][0] == 1:
                    return await all_handler(message) and False

            return one and two
        except:
            return False
