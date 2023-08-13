from typing import Callable, Awaitable, Dict, Any, Union

from aiogram import BaseMiddleware, html
from aiogram.dispatcher.flags import get_flag
from aiogram.fsm.storage.base import StorageKey

from aiogram.types import CallbackQuery, Message

from handlers.users.games.minesweeper.keyboards.kb_newgame import ClickCallbackFactory, SwitchFlagCallbackFactory, \
    SwitchModeCallbackFactory
from loader import bot


class CheckActiveGameMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: Dict[str, Any],
    ) -> Any:
        """
        Check whether game is active. This middleware is intended for CallbackQuery only!
        """
        need_check_handler = get_flag(data, "need_check_game")
        if not need_check_handler:
            return await handler(event, data)
        state = data["state"]
        user_data = await state.get_data()
        fsm_game_id = user_data.get("game_id")
        callback_data = data.get("callback_data")
        if event.from_user.id != callback_data.user_id:
            await event.answer(show_alert=False, text="💣 Это не твоя игра !")
            return
        if not fsm_game_id:
            await event.message.edit_text(
                text=f"{html.italic('💣 Эта игра больше недоступна')}",
                reply_markup=None
            )
            return
        else:
            if isinstance(callback_data, (ClickCallbackFactory, SwitchFlagCallbackFactory, SwitchModeCallbackFactory)):
                if callback_data.game_id != fsm_game_id:
                    await event.message.edit_text(
                        text=f"{html.italic('💣 Эта игра больше недоступна')}",
                        reply_markup=None
                    )
                    await event.answer(
                        text="💣 Эта игра недоступна, потому что есть более свежая!",
                        show_alert=True
                    )
                    return
        return await handler(event, data)


class CheckActiveGameBlackMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Union[Message, CallbackQuery], Dict[str, Any]], Awaitable[Any]],
            event: Union[Message, CallbackQuery],
            data: Dict[str, Any],
    ) -> Any:
        """
        Check whether game is active. This middleware is intended for CallbackQuery only!
        """
        need_check_handler = get_flag(data, "need_check_game")

        if not need_check_handler:
            return await handler(event, data)

        state = data["fsm_storage"]

        user_data = await state.get_data(key=StorageKey(
            user_id=event.from_user.id,
            chat_id=event.from_user.id,
            bot_id=bot.id))

        fsm_game_id = user_data.get("game_id")
        if not fsm_game_id:
            await event.message.edit_text(
                text=f"{html.italic(' Эта игра больше недоступна')}",
                reply_markup=None
            )
            return
        else:
            return await handler(event, data)
