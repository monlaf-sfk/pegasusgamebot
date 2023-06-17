import random
from contextlib import suppress
from typing import Callable, Awaitable, Dict, Any, Union

from aiogram import BaseMiddleware, html
from aiogram.dispatcher.flags import get_flag
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.storage.base import StorageKey

from aiogram.types import CallbackQuery, Message

from handlers.users.games.blackjack.state import GameBlackjackCallback, game_blackjacksplit_kb, get_hand_value, \
    get_card_value, game_blackjack_kb, NewGameCallbackBlackjack, game_blackjack_insurance_kb
from handlers.users.games.minesweeper.keyboards.kb_newgame import ClickCallbackFactory, SwitchFlagCallbackFactory, \
    SwitchModeCallbackFactory
from loader import bot

from utils.main.users import User


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


numbers_emoji = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']


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

        callback_data = data.get("callback_data")
        if event.from_user.id != callback_data.id:
            await event.answer(show_alert=False, text=" Это не твоя игра !")

            return
        user_data = await state.get_data(bot=bot, key=StorageKey(
            user_id=event.from_user.id,
            chat_id=event.from_user.id,
            bot_id=bot.id))

        fsm_game_id = user_data.get("game_id")
        player_hand = user_data.get("player_hand")
        player_hand2 = user_data.get("player_hand2")
        dealer_hand = user_data.get("dealer_hand")

        if not fsm_game_id and (
                callback_data.as_separate == False if isinstance(callback_data, NewGameCallbackBlackjack) else True):
            await event.message.edit_text(
                text=f"{html.italic(' Эта игра больше недоступна')}",
                reply_markup=None
            )
            return
        else:

            if isinstance(callback_data, GameBlackjackCallback):
                if callback_data.game_id != fsm_game_id:

                    user = User(user=event.from_user)
                    state_get = await state.get_state(bot=bot, key=StorageKey(
                        user_id=event.from_user.id,
                        chat_id=event.from_user.id,
                        bot_id=bot.id))
                    smile = ['♠', '🃏', '♣', '♥', '♦', '🎴']
                    rsmile = random.choice(smile)
                    if state_get == 'BlackjackGame:waiting_for_action':
                        if player_hand2:
                            text_player = '➖ 1-я рука:(текущая)\n'
                            for index, cards in enumerate(player_hand, start=1):
                                emoji = ''.join(numbers_emoji[int(i)] for i in str(index))
                                text_player += f'  {emoji} {cards}\n'
                            player_hand_value2 = get_hand_value(player_hand2)
                            text_player2 = '➖ 2-я рука:\n'
                            for index, cards in enumerate(player_hand2, start=1):
                                emoji = ''.join(numbers_emoji[int(i)] for i in str(index))
                                text_player2 += f'  {emoji} {cards}\n'
                            with suppress(TelegramBadRequest):
                                await event.message.edit_text(
                                    f"{rsmile} {user.link}, Нажмите на кнопки для продолжения::"
                                    f"\n🎫 Ваша руки: {get_hand_value(player_hand)} & {player_hand_value2}\n"
                                    f"{text_player}"
                                    f"{text_player2}"
                                    f"\n🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                                    f"\n 1️⃣ {dealer_hand[0]}"
                                    ,
                                    reply_markup=game_blackjack_kb(callback_data.game_id, event.from_user.id,
                                                                   split=True),
                                    disable_web_page_preview=True)
                            return
                        else:
                            kb = game_blackjack_kb(callback_data.game_id, event.from_user.id,
                                                   player_hand, dealer_hand) if get_card_value(
                                player_hand[0]) != get_card_value(
                                player_hand[1]) else game_blackjacksplit_kb(callback_data.game_id, event.from_user.id,
                                                                            dealer_hand)

                            text_player = '➖ 1-я рука:\n'
                            for index, cards in enumerate(player_hand, start=1):
                                emoji = ''.join(numbers_emoji[int(i)] for i in str(index))
                                text_player += f'  {emoji} {cards}\n'
                            with suppress(TelegramBadRequest):
                                await event.message.edit_text(
                                    f"{rsmile} {user.link}, Нажмите на кнопки для продолжения:"
                                    f"\n🎫 Ваша руки: {get_hand_value(player_hand)}\n"
                                    f"{text_player}"
                                    f"\n🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                                    f"\n 1️⃣ {dealer_hand[0]}"
                                    ,
                                    reply_markup=kb,
                                    disable_web_page_preview=True)
                            return
                    if state_get == 'BlackjackGame:waiting_for_action2':
                        if player_hand2:
                            text_player = '➖ 1-я рука:\n'
                            for index, cards in enumerate(player_hand, start=1):
                                emoji = ''.join(numbers_emoji[int(i)] for i in str(index))
                                text_player += f'  {emoji} {cards}\n'
                            player_hand_value2 = get_hand_value(player_hand2)
                            text_player2 = '➖ 2-я рука:(текущая)\n'
                            for index, cards in enumerate(player_hand2, start=1):
                                emoji = ''.join(numbers_emoji[int(i)] for i in str(index))
                                text_player2 += f'  {emoji} {cards}\n'
                            with suppress(TelegramBadRequest):
                                await event.message.edit_text(
                                    f"{rsmile} {user.link}, Нажмите на кнопки для продолжения::"
                                    f"\n🎫 Ваша руки: {get_hand_value(player_hand)} & {player_hand_value2}\n"
                                    f"{text_player}"
                                    f"{text_player2}"
                                    f"\n🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                                    f"\n 1️⃣ {dealer_hand[0]}"
                                    ,
                                    reply_markup=game_blackjack_kb(callback_data.game_id, event.from_user.id,
                                                                   split=True),
                                    disable_web_page_preview=True)
                            return
                        else:
                            kb = game_blackjack_kb(callback_data.game_id, event.from_user.id,
                                                   player_hand, dealer_hand) if get_card_value(
                                player_hand[0]) != get_card_value(
                                player_hand[1]) else game_blackjacksplit_kb(callback_data.game_id,
                                                                            event.from_user.id, dealer_hand)

                            text_player = '➖ 1-я рука:\n'
                            for index, cards in enumerate(player_hand, start=1):
                                emoji = ''.join(numbers_emoji[int(i)] for i in str(index))
                                text_player += f'  {emoji} {cards}\n'
                            with suppress(TelegramBadRequest):
                                await event.message.edit_text(
                                    f"{rsmile} {user.link}, Нажмите на кнопки для продолжения:"
                                    f"\n🎫 Ваша руки: {get_hand_value(player_hand)}\n"
                                    f"{text_player}"
                                    f"\n🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                                    f"\n 1️⃣ {dealer_hand[0]}"
                                    ,
                                    reply_markup=kb,
                                    disable_web_page_preview=True)
                            return
                    if state_get == 'BlackjackGame:waiting_for_action3':

                        text_player = '➖ 1-я рука:\n'
                        for index, cards in enumerate(player_hand, start=1):
                            emoji = ''.join(numbers_emoji[int(i)] for i in str(index))
                            text_player += f'  {emoji} {cards}\n'
                        with suppress(TelegramBadRequest):
                            await event.message.edit_text(
                                f"{rsmile} {user.link}, Нажмите на кнопки для продолжения:"
                                f"\n🎫 Ваша руки: {get_hand_value(player_hand)}\n"
                                f"{text_player}"
                                f"\n🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                                f"\n 1️⃣ {dealer_hand[0]}"
                                ,
                                reply_markup=game_blackjack_insurance_kb(callback_data.game_id, event.from_user.id),
                                disable_web_page_preview=True)
                        return
        return await handler(event, data)
