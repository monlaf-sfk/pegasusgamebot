import time

from aiogram.filters import BaseFilter
from aiogram.types import Message

from config import owner_id
from utils.main.users import User


class IsBan(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if message.from_user.is_bot == True:
            return
        user = User(user=message.from_user)
        return user.ban


class IsBeta(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if message.from_user.is_bot == True:
            return
        user = User(user=message.from_user)
        donate = user.donate
        return donate and donate.id > 1


class IsPremium(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if message.from_user.is_bot == True:
            return
        user = User(user=message.from_user)
        donate = user.donate
        return donate and donate.id > 2


class IsElite(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if message.from_user.is_bot == True:
            return
        user = User(user=message.from_user)
        donate = user.donate
        return donate and donate.id > 3


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if message.from_user.is_bot == True:
            return
        user = User(user=message.from_user)
        donate = user.donate
        return donate and donate.id > 4 or message.from_user.id == owner_id


last_use = {}


async def flood_handler(message: Message):
    if message.from_user.is_bot == True:
        return
    if last_use.get(message.from_user.id):
        if time.time() - last_use[message.from_user.id] < 1.5:
            return False
    last_use[message.from_user.id] = time.time()
    return True


last_use2 = {}


async def flood_handler2(message: Message):
    if message.from_user.is_bot == True:
        return
    if last_use2.get(message.from_user.id):
        if time.time() - last_use2[message.from_user.id] < 3:
            await message.reply("⏰ Играть можно раз в 3 сек !")
            return False
    last_use2[message.from_user.id] = time.time()
    return True
