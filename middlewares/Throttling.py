from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message, CallbackQuery
from cachetools import TTLCache

THROTTLE_TIME_GAME = 1.5
THROTTLE_TIME_OTHER = 1
THROTTLE_TIME_OTHER2 = 0.5


class ThrottlingMiddleware(BaseMiddleware):
    caches = {
        "games": TTLCache(maxsize=10_000, ttl=THROTTLE_TIME_GAME),
        "default": TTLCache(maxsize=10_000, ttl=THROTTLE_TIME_OTHER),
        None: TTLCache(maxsize=10_000, ttl=THROTTLE_TIME_OTHER2)
    }

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any],
    ) -> Any:
        throttling_key = get_flag(data, "throttling_key")

        if event.new_chat_members:
            return await handler(event, data)
        if throttling_key in self.caches:
            if event.from_user.id in self.caches[throttling_key]:
                return
            else:
                self.caches[throttling_key][event.from_user.id] = None
        return await handler(event, data)


class ThrottlingCallMiddleware(BaseMiddleware):
    caches = {
        "games": TTLCache(maxsize=10_000, ttl=THROTTLE_TIME_GAME),
        "default": TTLCache(maxsize=10_000, ttl=THROTTLE_TIME_OTHER),
        None: TTLCache(maxsize=10_000, ttl=THROTTLE_TIME_OTHER2)
    }

    async def __call__(
            self,
            handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: Dict[str, Any],
    ) -> Any:
        throttling_key = get_flag(data, "throttling_key")

        if throttling_key in self.caches:
            if event.from_user.id in self.caches[throttling_key]:
                return
            else:
                self.caches[throttling_key][event.from_user.id] = None
        return await handler(event, data)
