from aiogram.filters import BaseFilter
from aiogram.types import Message

from config import owner_id


class IsOwner(BaseFilter):
    async def __call__(self, message: Message) -> bool:  # [3]

        return message.from_user.id == owner_id


class IsBot(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.new_chat_members[-1].id == message.bot.id
