from aiogram.filters import BaseFilter
from aiogram.types import Message
from cachetools import TTLCache

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


last_use = {
    "last": TTLCache(maxsize=10_000, ttl=1),
}


async def flood_handler(message: Message):
    if message.from_user.is_bot == True:
        return
    if message.from_user.id in last_use['last']:
        return False
    else:
        last_use['last'][message.from_user.id] = True
        return True


last_use2 = {
    "last": TTLCache(maxsize=10_000, ttl=1),
}


async def flood_handler2(message: Message):
    if message.from_user.is_bot == True:
        return
    if message.from_user.id in last_use2['last']:
        return False
    else:
        last_use2['last'][message.from_user.id] = True
        return True
