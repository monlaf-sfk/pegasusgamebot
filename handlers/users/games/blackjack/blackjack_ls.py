import random
from contextlib import suppress
from uuid import uuid4

from aiogram import flags, Bot, Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey, BaseStorage
from aiogram.types import Message, CallbackQuery

from config import bot_name
from filters.triggers import Trigger
from filters.users import flood_handler2, flood_handler
from handlers.users.games.blackjack.help_func import get_numerate_cards, get_hand_value, get_card_value, numbers_emoji, \
    check_win, check_result, create_deck
from handlers.users.games.blackjack.state import game_blackjacksplit_kb, game_blackjack_kb, BlackjackGame, to_str3
from keyboard.generate import show_balance_kb

from utils.main.cash import to_str, get_cash
from utils.main.users import User

router = Router()
router.message.filter(F.chat.type.in_({"group", "supergroup"}))
router.callback_query.filter(F.chat.type.in_({"group", "supergroup"}))


async def check_state2(message: Message, state: FSMContext, fsm_storage: BaseStorage, bot: Bot):
    user = User(id=message.from_user.id if message.from_user.id else message.from_user.id)
    smile = ['♠', '🃏', '♣', '♥', '♦', '🎴']
    rsmile = random.choice(smile)
    if isinstance(message, CallbackQuery):

        state_get = await fsm_storage.get_state(bot=bot, key=StorageKey(
            user_id=message.from_user.id,
            chat_id=message.from_user.id,
            bot_id=bot.id))
        if state_get == 'BlackjackGame:waiting_for_action':
            user_data = await fsm_storage.get_data(bot=bot, key=StorageKey(
                user_id=message.from_user.id,
                chat_id=message.from_user.id,
                bot_id=bot.id))
            player_hand = user_data.get("player_hand")
            player_hand2 = user_data.get("player_hand2")
            dealer_hand = user_data.get("dealer_hand")

            if player_hand2:
                text_player = f'➖ 1-я рука - (Текущая): \n{await get_numerate_cards(player_hand)}'
                text_player2 = f'➖ 2-я рука: \n{await get_numerate_cards(player_hand2)}'
                text_dil = f'{await get_numerate_cards(dealer_hand)}'

                await message.message.reply(
                    f"{rsmile} {user.link},выберите действие: «Блэкджек [еще/стоп/сплит/удвоить]»"
                    f"\n🎫 Ваша руки: {get_hand_value(player_hand)} & {get_hand_value(player_hand2)}\n"
                    f"{text_player}"
                    f"{text_player2}"
                    f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                    f"\n{text_dil}"
                    ,

                    disable_web_page_preview=True)
                return
            else:

                text_player = f'➖ 1-я рука: \n{await get_numerate_cards(player_hand)}'
                text_dil = f'{await get_numerate_cards(dealer_hand)}'
                await message.message.reply(
                    f"{rsmile} {user.link}, выберите действие: «Блэкджек [еще/стоп/сплит/удвоить]»"
                    f"\n🎫 Ваша руки: {get_hand_value(player_hand)}\n"
                    f"{text_player}"
                    f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                    f"\n{text_dil}"
                    ,

                    disable_web_page_preview=True)
                return
        if state_get == 'BlackjackGame:waiting_for_action2':
            user_data = await fsm_storage.get_data(bot=bot, key=StorageKey(
                user_id=message.from_user.id,
                chat_id=message.from_user.id,
                bot_id=bot.id))

            player_hand = user_data.get("player_hand")
            player_hand2 = user_data.get("player_hand2")
            dealer_hand = user_data.get("dealer_hand")

            if player_hand2:
                text_player = f'➖ 1-я рука: \n{await get_numerate_cards(player_hand)}'
                text_player2 = f'➖ 2-я рука - (Текущая): \n{await get_numerate_cards(player_hand2)}'
                text_dil = f'{await get_numerate_cards(dealer_hand)}'

                await message.message.reply(
                    f"{rsmile} {user.link}, выберите действие: «Блэкджек [еще/стоп/сплит/удвоить]»"
                    f"\n🎫 Ваша руки: {get_hand_value(player_hand)} & {get_hand_value(player_hand2)}\n"
                    f"{text_player}"
                    f"{text_player2}"
                    f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                    f"\n{text_dil}"
                    ,

                    disable_web_page_preview=True)
                return
            else:

                text_player = f'➖ 1-я рука: \n{await get_numerate_cards(player_hand)}'
                text_dil = f'{await get_numerate_cards(dealer_hand)}'
                await message.message.reply(
                    f"{user.link}, выберите действие: «Блэкджек [еще/стоп/сплит/удвоить]»"
                    f"\n🎫 Ваша руки: {get_hand_value(player_hand)}\n"
                    f"{text_player}"
                    f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                    f"\n{text_dil}"
                    ,

                    disable_web_page_preview=True)
                return
        if state_get == 'BlackjackGame:waiting_for_action3':

            user_data = await fsm_storage.get_data(bot=bot, key=StorageKey(
                user_id=message.from_user.id,
                chat_id=message.from_user.id,
                bot_id=bot.id))

            player_hand = user_data.get("player_hand")
            dealer_hand = user_data.get("dealer_hand")
            text_player = '➖ 1-я рука:\n'
            for index, cards in enumerate(player_hand, start=1):
                emoji = ''.join(numbers_emoji[int(i)] for i in str(index))
                text_player += f'  {emoji} {cards}\n'
            with suppress(TelegramBadRequest):
                await message.message.reply(
                    f"{rsmile} {user.link}, выберите действие: «Блэкджек [еще/стоп/сплит/удвоить]»"
                    f"\n🎫 Ваша руки: {get_hand_value(player_hand)}\n"
                    f"{text_player}"
                    f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                    f"\n 1️⃣ {dealer_hand[0]}"
                    ,

                    disable_web_page_preview=True)
            return
    state_get = await fsm_storage.get_state(bot=bot, key=StorageKey(
        user_id=message.from_user.id,
        chat_id=message.from_user.id,
        bot_id=bot.id))

    if state_get == 'BlackjackGame:waiting_for_action':
        user_data = await fsm_storage.get_data(bot=bot, key=StorageKey(
            user_id=message.from_user.id,
            chat_id=message.from_user.id,
            bot_id=bot.id))

        player_hand = user_data.get("player_hand")
        player_hand2 = user_data.get("player_hand2")
        dealer_hand = user_data.get("dealer_hand")

        if player_hand2:
            text_player = f'➖ 1-я рука - (Текущая): \n{await get_numerate_cards(player_hand)}'
            text_player2 = f'➖ 2-я рука: \n{await get_numerate_cards(player_hand2)}'
            text_dil = f'{await get_numerate_cards(dealer_hand)}'

            await message.reply(
                f"{rsmile} {user.link}, выберите действие: «Блэкджек [еще/стоп/сплит/удвоить]»"
                f"\n🎫 Ваша руки: {get_hand_value(player_hand)} & {get_hand_value(player_hand2)}\n"
                f"{text_player}"
                f"{text_player2}"
                f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                f"\n{text_dil}"
                ,

                disable_web_page_preview=True)
            return
        else:

            text_player = f'➖ 1-я рука: \n{await get_numerate_cards(player_hand)}'

            text_dil = f'{await get_numerate_cards(dealer_hand)}'
            await message.reply(
                f"{rsmile} {user.link}, выберите действие: «Блэкджек [еще/стоп/сплит/удвоить]»"
                f"\n🎫 Ваша руки: {get_hand_value(player_hand)}\n"
                f"{text_player}"
                f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                f"\n{text_dil}"
                ,

                disable_web_page_preview=True)
            return
    if state_get == 'BlackjackGame:waiting_for_action2':
        user_data = await fsm_storage.get_data(bot=bot, key=StorageKey(
            user_id=message.from_user.id,
            chat_id=message.from_user.id,
            bot_id=bot.id))

        player_hand = user_data.get("player_hand")
        player_hand2 = user_data.get("player_hand2")
        dealer_hand = user_data.get("dealer_hand")

        if player_hand2:
            text_player = f'➖ 1-я рука: \n{await get_numerate_cards(player_hand)}'
            text_player2 = f'➖ 2-я рука - (Текущая): \n{await get_numerate_cards(player_hand2)}'
            text_dil = f'{await get_numerate_cards(dealer_hand)}'

            await message.reply(
                f"{rsmile} {user.link}, выберите действие: «Блэкджек [еще/стоп/сплит/удвоить]»"
                f"\n🎫 Ваша руки: {get_hand_value(player_hand)} & {get_hand_value(player_hand2)}\n"
                f"{text_player}"
                f"{text_player2}"
                f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                f"\n{text_dil}"
                ,

                disable_web_page_preview=True)
            return
        else:

            text_player = f'➖ 1-я рука: \n{await get_numerate_cards(player_hand)}'
            text_dil = f'{await get_numerate_cards(dealer_hand)}'
            await message.reply(
                f"{rsmile} {user.link}, выберите действие: «Блэкджек [еще/стоп/сплит/удвоить]»"
                f"\n🎫 Ваша руки: {get_hand_value(player_hand)}\n"
                f"{text_player}"
                f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                f"\n{text_dil}"
                ,
                disable_web_page_preview=True)
            return
    if state_get == 'BlackjackGame:waiting_for_action3':
        user_data = await fsm_storage.get_data(bot=bot, key=StorageKey(
            user_id=message.from_user.id,
            chat_id=message.from_user.id,
            bot_id=bot.id))

        player_hand = user_data.get("player_hand")
        dealer_hand = user_data.get("dealer_hand")
        text_player = '➖ 1-я рука:\n'
        for index, cards in enumerate(player_hand, start=1):
            emoji = ''.join(numbers_emoji[int(i)] for i in str(index))
            text_player += f'  {emoji} {cards}\n'
        with suppress(TelegramBadRequest):
            await message.reply(
                f"{rsmile} {user.link}, выберите действие: «Блэкджек [еще/стоп/сплит/удвоить]»"
                f"\n🎫 Ваша руки: {get_hand_value(player_hand)}\n"
                f"{text_player}"
                f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                f"\n 1️⃣ {dealer_hand[0]}"
                ,
                disable_web_page_preview=True)
        return


@router.message(Trigger(["бд еще", "бд стоп", "бд удвоить", "бд сплит", "бд отказ", "бд страховка"]),
                BlackjackGame.waiting_for_action)
async def action_blackjack_ls(message: Message, state: FSMContext,
                              fsm_storage: BaseStorage, bot: Bot):
    data = await fsm_storage.get_data(bot=bot, key=StorageKey(
        user_id=message.from_user.id,
        chat_id=message.from_user.id,
        bot_id=bot.id))
    summ5 = data.get("summ")
    deck = data.get("deck")
    player_hand = data.get("player_hand")
    player_hand2 = data.get("player_hand2")
    dealer_hand = data.get("dealer_hand")

    user = User(user=message.from_user)
    if user.balance < summ5:
        return await message.answer('❌ Ошибка. Недостаточно денег на руках для ставки! 💸'
                                    f'💰Требуется: {to_str3(summ5)} ', show_alert=True)
    smile = ['♠', '🃏', '♣', '♥', '♦', '🎴']
    rsmile = random.choice(smile)
    try:
        action = message.text.split()[1]
    except:
        state_get = await fsm_storage.get_state(bot=bot, key=StorageKey(
            user_id=message.from_user.id,
            chat_id=message.from_user.id,
            bot_id=bot.id))
        if state_get == 'BlackjackGame:waiting_for_action':
            return await check_state2(message, state, fsm_storage, bot)
        if state_get == 'BlackjackGame:waiting_for_action2':
            return await check_state2(message, state, fsm_storage, bot)
        if state_get == 'BlackjackGame:waiting_for_action3':
            return await check_state2(message, state, fsm_storage, bot)

    if action == "сплит":
        if get_card_value(player_hand[0]) != get_card_value(player_hand[1]):
            text_player = f'➖ 1-я рука: \n{await get_numerate_cards(player_hand)}'
            with suppress(TelegramBadRequest):
                await message.reply(
                    f"{rsmile} {user.link}, разделять можно только пару одного достоинства 👍🏻:"
                    f"\n🎫 Ваша рука: {get_hand_value(player_hand)}"
                    f"\n{text_player}",
                    disable_web_page_preview=True)
            return
        if user.balance < summ5 * 2:
            text_player = f'➖ 1-я рука: \n{await get_numerate_cards(player_hand)}'
            text_dil = f'{await get_numerate_cards(dealer_hand)}'
            with suppress(TelegramBadRequest):
                await message.reply(
                    f"{rsmile} {user.link},Для разделения требуется({to_str(summ5 * 2)}):"
                    f"\n🎫 Ваша рука: {get_hand_value(player_hand)}"
                    f"\n{text_player}"
                    f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                    f"\n{text_dil}"
                    ,

                    disable_web_page_preview=True)
            return
        player_hand2.append(player_hand[1])
        player_hand2.append(deck.pop())
        player_hand.pop()
        player_hand.append(deck.pop())

        text_player = f'➖ 1-я рука - (Текущая): \n{await get_numerate_cards(player_hand)}'
        text_player2 = f'➖ 2-я рука: \n{await get_numerate_cards(player_hand2)}'
        text_dil = f'{await get_numerate_cards(dealer_hand)}'

        with suppress(TelegramBadRequest):
            await message.reply(f"{rsmile} {user.link} , Ваши очки:"
                                f"\n🎫 Ваши руки: {get_hand_value(player_hand)} & {get_hand_value(player_hand2)}\n"
                                f"{text_player}"
                                f"{text_player2}"
                                f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                                f"\n {text_dil}"
                                ,
                                disable_web_page_preview=True)
            newgamedata_dict = {"deck": deck, 'player_hand': player_hand, 'player_hand2': player_hand2,
                                'dealer_hand': dealer_hand}

            await fsm_storage.update_data(bot=bot, data=newgamedata_dict, key=StorageKey(
                user_id=message.from_user.id,
                chat_id=message.from_user.id,
                bot_id=bot.id))
            await fsm_storage.set_state(bot=bot, state=BlackjackGame.waiting_for_action, key=StorageKey(
                user_id=message.from_user.id,
                chat_id=message.from_user.id,
                bot_id=bot.id))

        return
    if action == "еще":

        if player_hand2:
            player_hand_value2 = get_hand_value(player_hand2)
            text_player2 = f'➖ 2-я рука: \n{await get_numerate_cards(player_hand2)}'
            if user.balance < summ5 * 2:
                text_player = f'➖ 1-я рука - (Текущая): \n{await get_numerate_cards(player_hand)}'
                text_dil = f'{await get_numerate_cards(dealer_hand)}'

                with suppress(TelegramBadRequest):
                    await message.reply(
                        f"{rsmile} {user.link},Для продолжения требуется({to_str(summ5 * 2)}):"
                        f"\n🎫 Ваша руки: {get_hand_value(player_hand)} & {player_hand_value2}\n"
                        f"{text_player}"
                        f"{text_player2}"
                        f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                        f"\n {text_dil}"
                        ,

                        disable_web_page_preview=True)
                return
            player_hand.append(deck.pop())
            player_hand_value = get_hand_value(player_hand)

            if player_hand_value > 21:
                text_player = f'➖ 1-я рука: \n{await get_numerate_cards(player_hand)}'
                text_player2 = f'➖ 2-я рука - (Текущая): \n{await get_numerate_cards(player_hand2)}'
                text_dil = f'{await get_numerate_cards(dealer_hand)}'
                with suppress(TelegramBadRequest):

                    await message.reply(f"{rsmile} {user.link},Вы вытянули {player_hand[-1]}: "
                                        f"\n🎫 Ваша рука: {player_hand_value} & {player_hand_value2}\n"
                                        f"{text_player}"
                                        f"{text_player2}"
                                        f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                                        f"\n {text_dil}"
                                        ,

                                        disable_web_page_preview=True)
                    newgamedata_dict = {"deck": deck, 'player_hand': player_hand, 'player_hand2': player_hand2,
                                        'dealer_hand': dealer_hand}
                    await fsm_storage.update_data(bot=bot, data=newgamedata_dict, key=StorageKey(
                        user_id=message.from_user.id,
                        chat_id=message.from_user.id,
                        bot_id=bot.id))
                    await fsm_storage.set_state(bot=bot, state=BlackjackGame.waiting_for_action2, key=StorageKey(
                        user_id=message.from_user.id,
                        chat_id=message.from_user.id,
                        bot_id=bot.id))

                return
            else:
                with suppress(TelegramBadRequest):
                    text_player = f'➖ 1-я рука - (Текущая): \n{await get_numerate_cards(player_hand)}'
                    text_player2 = f'➖ 2-я рука: \n{await get_numerate_cards(player_hand2)}'
                    text_dil = f'{await get_numerate_cards(dealer_hand)}'
                    await message.reply(f"{rsmile} {user.link},Вы вытянули {player_hand[-1]}:"
                                        f"\n🎫 Ваша рука: {player_hand_value} & {player_hand_value2}\n"
                                        f"{text_player}"
                                        f"{text_player2}"
                                        f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                                        f"\n{text_dil}"
                                        ,
                                        disable_web_page_preview=True)

                    newgamedata_dict = {"deck": deck, 'player_hand': player_hand, 'player_hand2': player_hand2,
                                        'dealer_hand': dealer_hand}
                    await fsm_storage.update_data(bot=bot, data=newgamedata_dict, key=StorageKey(
                        user_id=message.from_user.id,
                        chat_id=message.from_user.id,
                        bot_id=bot.id))
                    await fsm_storage.set_state(bot=bot, state=BlackjackGame.waiting_for_action, key=StorageKey(
                        user_id=message.from_user.id,
                        chat_id=message.from_user.id,
                        bot_id=bot.id))

                return

        player_hand.append(deck.pop())
        player_hand_value = get_hand_value(player_hand)
        text_player = '➖ 1-я рука:\n'
        for index, cards in enumerate(player_hand, start=1):
            emoji = ''.join(numbers_emoji[int(i)] for i in str(index))
            text_player += f'  {emoji} {cards}\n'
        if player_hand_value > 21:
            with suppress(TelegramBadRequest):

                await message.reply(f"{rsmile} {user.link},Вы вытянули {player_hand[-1]}: "
                                    f"\n🎫 Ваша рука: {player_hand_value}\n"
                                    f"{text_player}"
                                    f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                                    f"\n 1️⃣ {dealer_hand[0]}"
                                    f"\nПровал! Вы проиграли!\n"
                                    f"вы потеряли {to_str(summ5)}!",

                                    disable_web_page_preview=True)
                user.edit('balance', user.balance - summ5)
                await state.clear()
            return
        else:
            with suppress(TelegramBadRequest):
                await message.reply(f"{rsmile} {user.link},Вы вытянули {player_hand[-1]}:"
                                    f"\n🎫 Ваша рука: {get_hand_value(player_hand)}\n"
                                    f"{text_player}"
                                    f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                                    f"\n 1️⃣ {dealer_hand[0]}"
                                    ,
                                    disable_web_page_preview=True)
                newgamedata_dict = {"deck": deck, 'player_hand': player_hand,
                                    'dealer_hand': dealer_hand}
                await fsm_storage.update_data(bot=bot, data=newgamedata_dict, key=StorageKey(
                    user_id=message.from_user.id,
                    chat_id=message.from_user.id,
                    bot_id=bot.id))

            return

    if action == 'стоп':
        if player_hand2:
            text_player = f'➖ 1-я рука:\n{await get_numerate_cards(player_hand)}'

            text_player2 = f'➖ 2-я рука:(текущая)\n{await get_numerate_cards(player_hand2)}'

            if user.balance < summ5 * 2:
                with suppress(TelegramBadRequest):
                    text_dil = f'{await get_numerate_cards(dealer_hand)}'
                    await message.reply(
                        f"{rsmile} {user.link},Для продолжения требуется({to_str(summ5 * 2)}):"
                        f"\n🎫 Ваша руки: {get_hand_value(player_hand)} & {get_hand_value(player_hand2)}\n"
                        f"{text_player}"
                        f"{text_player2}"
                        f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                        f"\n {text_dil}"
                        ,

                        disable_web_page_preview=True)
                return
            with suppress(TelegramBadRequest):
                text_dil = f'{await get_numerate_cards(dealer_hand)}'
                await message.reply(f"{rsmile} {user.link}:"
                                    f"\n🎫 Ваша руки: {get_hand_value(player_hand)} & {get_hand_value(player_hand2)}\n"
                                    f"{text_player}"
                                    f"{text_player2}"
                                    f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                                    f"\n {text_dil}"
                                    ,
                                    disable_web_page_preview=True)
                newgamedata_dict = {"deck": deck, 'player_hand': player_hand, 'player_hand2': player_hand2,
                                    'dealer_hand': dealer_hand}
                await fsm_storage.update_data(bot=bot, data=newgamedata_dict, key=StorageKey(
                    user_id=message.from_user.id,
                    chat_id=message.from_user.id,
                    bot_id=bot.id))

                await fsm_storage.set_state(bot=bot, state=BlackjackGame.waiting_for_action2, key=StorageKey(
                    user_id=message.from_user.id,
                    chat_id=message.from_user.id,
                    bot_id=bot.id))
            return
        dealer_hand_value = get_hand_value(dealer_hand)
        while dealer_hand_value < 17:
            dealer_hand.append(deck.pop())
            dealer_hand_value = get_hand_value(dealer_hand)
        result = await check_win(player_hand, dealer_hand, user.id, summ5)
        with suppress(TelegramBadRequest):
            await message.reply(result,

                                disable_web_page_preview=True)

        return await state.clear()
    if action == 'удвоить':
        if user.balance < summ5 * 2:
            text_player = f'➖ 1-я рука:\n{await get_numerate_cards(player_hand)}'
            text_dil = f'{await get_numerate_cards(dealer_hand)}'
            with suppress(TelegramBadRequest):
                return await message.reply(
                    f"{rsmile} {user.link},Для удвоения требуется({to_str(summ5 * 2)}):"
                    f"\n🎫 Ваша рука: {get_hand_value(player_hand)}\n"
                    f"{text_player}"

                    f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                    f"\n {text_dil}"
                    ,

                    disable_web_page_preview=True)
            return
        player_hand.append(deck.pop())
        dealer_hand_value = get_hand_value(dealer_hand)
        while dealer_hand_value < 17:
            dealer_hand.append(deck.pop())
            dealer_hand_value = get_hand_value(dealer_hand)
        with suppress(TelegramBadRequest):
            result = await check_win(player_hand, dealer_hand, user.id, summ5 * 2)
            await message.reply(result,

                                disable_web_page_preview=True)

        return await state.clear()

    if action == 'отказ':
        user.edit('balance', user.balance - round(summ5 / 2))
        with suppress(TelegramBadRequest):
            text_player = f'➖ 1-я рука:\n{await get_numerate_cards(player_hand)}'
            text_dil = f'{await get_numerate_cards(dealer_hand)}'
            await message.reply(
                f"{rsmile} {user.link}:"
                f"\n🎫 Ваша рука: {get_hand_value(player_hand)}\n"
                f"{text_player}"
                f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                f"\n {text_dil}"
                f"\n\n🚫 Вы отказались от игры и потеряли половину своей суммы!"
                ,

                disable_web_page_preview=True)

        return await state.clear()
    if action == 'страховка':
        text_player = f'➖ 1-я рука: \n{await get_numerate_cards(player_hand)}'
        text_dil = f'{await get_numerate_cards(dealer_hand)}'
        if dealer_hand and get_card_value(dealer_hand[0]) != 11:
            with suppress(TelegramBadRequest):
                await message.reply(
                    f"{rsmile} {user.link}, Доступно только при наличии у бота туза :"
                    f"\n🎫 Ваша рука: {get_hand_value(player_hand)}"
                    f"\n{text_player}"
                    f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                    f"\n{text_dil}"
                    , disable_web_page_preview=True)
            return
        if user.balance < (round(summ5 / 2)) + summ5:
            with suppress(TelegramBadRequest):
                await message.reply(
                    f"{rsmile} {user.link}, для страхования дополнительно требуется ({to_str(round(summ5 / 2))}):"
                    f"\n🎫 Ваша рука: {get_hand_value(player_hand)}"
                    f"\n{text_player}"
                    f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                    f"\n{text_dil}"
                    ,

                    disable_web_page_preview=True)
            return
        with suppress(TelegramBadRequest):
            await message.reply(
                f"{rsmile} {user.link}:"
                f"\n🎫 Ваша рука: {get_hand_value(player_hand)}\n"
                f"{text_player}"
                f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                f"\n {text_dil}"
                f"\n\nВы застраховали свою ставку за {to_str(round(summ5 / 2))} 👍🏼!"
                ,

                disable_web_page_preview=True)
        newgamedata_dict = {"deck": deck, 'player_hand': player_hand,
                            'dealer_hand': dealer_hand, 'insurance': round(summ5 / 2)}
        await fsm_storage.update_data(bot=bot, data=newgamedata_dict, key=StorageKey(
            user_id=message.from_user.id,
            chat_id=message.from_user.id,
            bot_id=bot.id))
        await fsm_storage.set_state(bot=bot, state=BlackjackGame.waiting_for_action3, key=StorageKey(
            user_id=message.from_user.id,
            chat_id=message.from_user.id,
            bot_id=bot.id))


@router.message(Trigger(["бд еще", "бд стоп"]),
                BlackjackGame.waiting_for_action2)
async def action2_blackjack_ls(message: Message, state: FSMContext,
                               fsm_storage: BaseStorage, bot: Bot):
    data = await fsm_storage.get_data(bot=bot, key=StorageKey(
        user_id=message.from_user.id,
        chat_id=message.from_user.id,
        bot_id=bot.id))
    summ5 = data.get("summ")
    deck = data.get("deck")

    player_hand = data.get("player_hand")
    dealer_hand = data.get("dealer_hand")
    player_hand2 = data.get("player_hand2")

    user = User(user=message.from_user)
    if user.balance < summ5 * 2:
        return await message.answer('❌ Ошибка. Недостаточно денег на руках для ставки! 💸'
                                    f'💰Требуется: {to_str3(summ5 * 2)} ', show_alert=True)
    smile = ['♠', '🃏', '♣', '♥', '♦', '🎴']
    rsmile = random.choice(smile)
    try:
        action = message.text.split()[1]

    except:
        state_get = await fsm_storage.get_state(bot=bot, key=StorageKey(
            user_id=message.from_user.id,
            chat_id=message.from_user.id,
            bot_id=bot.id))
        if state_get == 'BlackjackGame:waiting_for_action':
            return await check_state2(message, state, fsm_storage, bot)
        if state_get == 'BlackjackGame:waiting_for_action2':
            return await check_state2(message, state, fsm_storage, bot)
        if state_get == 'BlackjackGame:waiting_for_action3':
            return await check_state2(message, state, fsm_storage, bot)
    if action == "еще":
        player_hand2.append(deck.pop())
        player_hand_value2 = get_hand_value(player_hand2)
        text_player2 = f'➖ 2-я рука:(текущая)\n{await get_numerate_cards(player_hand2)}'

        if user.balance < summ5 * 2:
            text_diller = f'{await get_numerate_cards(dealer_hand)}'
            text_player = f'➖ 1-я рука:\n{await get_numerate_cards(player_hand)}'
            with suppress(TelegramBadRequest):
                await message.reply(
                    f"{rsmile} {user.link},Для продолжения требуется({to_str(summ5 * 2)}):"
                    f"\n🎫 Ваша руки: {get_hand_value(player_hand)} & {player_hand_value2}\n"
                    f"{text_player}"
                    f"{text_player2}"
                    f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                    f"\n{text_diller} "
                    ,

                    disable_web_page_preview=True)
            return
        player_hand_value2 = get_hand_value(player_hand2)
        text_player = f'➖ 1-я рука:\n{await get_numerate_cards(player_hand)}'
        if player_hand_value2 > 21:
            dealer_hand_value = get_hand_value(dealer_hand)
            while dealer_hand_value < 17:
                dealer_hand.append(deck.pop())
                dealer_hand_value = get_hand_value(dealer_hand)
            result = await check_result(player_hand, player_hand2, dealer_hand, user.id, summ5)
            with suppress(TelegramBadRequest):
                await message.reply(result,

                                    disable_web_page_preview=True)

                await state.clear()
            return

        else:
            with suppress(TelegramBadRequest):
                await message.reply(f"{rsmile} {user.link},Вы вытянули {player_hand[-1]}:"
                                    f"\n🎫 Ваша рука: {get_hand_value(player_hand)} & {get_hand_value(player_hand2)}\n"
                                    f"{text_player}"
                                    f"{text_player2}"
                                    f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                                    f"\n 1️⃣ {dealer_hand[0]}"
                                    ,
                                    disable_web_page_preview=True)

                newgamedata_dict = {"deck": deck, 'player_hand': player_hand, 'player_hand2': player_hand2,
                                    'dealer_hand': dealer_hand}
                await fsm_storage.update_data(bot=bot, data=newgamedata_dict, key=StorageKey(
                    user_id=message.from_user.id,
                    chat_id=message.from_user.id,
                    bot_id=bot.id))
                await fsm_storage.set_state(bot=bot, state=BlackjackGame.waiting_for_action2, key=StorageKey(
                    user_id=message.from_user.id,
                    chat_id=message.from_user.id,
                    bot_id=bot.id))

        return
    if action == 'стоп':
        dealer_hand_value = get_hand_value(dealer_hand)
        while dealer_hand_value < 17:
            dealer_hand.append(deck.pop())
            dealer_hand_value = get_hand_value(dealer_hand)
        result = await check_result(player_hand, player_hand2, dealer_hand, user.id, summ5)
        with suppress(TelegramBadRequest):
            await message.reply(result,

                                disable_web_page_preview=True)
            await state.clear()
        return


@router.message(Trigger(["бд еще", "бд стоп", "бд удвоить"]),
                BlackjackGame.waiting_for_action3)
async def action3_blackjack(message: Message, state: FSMContext,
                            fsm_storage: BaseStorage, bot: Bot):
    data = await fsm_storage.get_data(bot=bot, key=StorageKey(
        user_id=message.from_user.id,
        chat_id=message.from_user.id,
        bot_id=bot.id))
    insurance = data.get("insurance")
    summ5 = data.get("summ")
    deck = data.get("deck")

    player_hand = data.get("player_hand")
    dealer_hand = data.get("dealer_hand")
    action = message.text.split()[1]
    user = User(user=message.from_user)
    if user.balance < summ5 + insurance:
        return await message.answer('❌ Ошибка. Недостаточно денег на руках для ставки! 💸'
                                    f'💰Требуется: {to_str3(summ5 + insurance)} ', show_alert=True)
    smile = ['♠', '🃏', '♣', '♥', '♦', '🎴']
    rsmile = random.choice(smile)
    if action == "еще":
        player_hand.append(deck.pop())
        player_hand_value = get_hand_value(player_hand)
        text_player = '➖ 1-я рука:\n'
        for index, cards in enumerate(player_hand, start=1):
            emoji = ''.join(numbers_emoji[int(i)] for i in str(index))
            text_player += f'  {emoji} {cards}\n'
        if player_hand_value > 21:
            with suppress(TelegramBadRequest):

                await message.reply(f"{rsmile} {user.link},Вы вытянули {player_hand[-1]}: "
                                    f"\n🎫 Ваша рука: {player_hand_value}\n"
                                    f"{text_player}"
                                    f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                                    f"\n 1️⃣ {dealer_hand[0]}"
                                    f"\nПровал! Вы проиграли!\n"
                                    f"вы потеряли {to_str(summ5)}!",

                                    disable_web_page_preview=True)
                user.edit('balance', user.balance - summ5 + insurance)
                await state.clear()
            return
        else:
            with suppress(TelegramBadRequest):
                await message.reply(f"{rsmile} {user.link},Вы вытянули {player_hand[-1]}:"
                                    f"\n🎫 Ваша рука: {get_hand_value(player_hand)}\n"
                                    f"{text_player}"
                                    f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                                    f"\n 1️⃣ {dealer_hand[0]}"
                                    ,
                                    disable_web_page_preview=True)
                newgamedata_dict = {"deck": deck, 'player_hand': player_hand,
                                    'dealer_hand': dealer_hand}
                await fsm_storage.update_data(bot=bot, data=newgamedata_dict, key=StorageKey(
                    user_id=message.from_user.id,
                    chat_id=message.from_user.id,
                    bot_id=bot.id))
                await fsm_storage.set_state(bot=bot, state=BlackjackGame.waiting_for_action3, key=StorageKey(
                    user_id=message.from_user.id,
                    chat_id=message.from_user.id,
                    bot_id=bot.id))
            return
    if action == 'стоп':
        dealer_hand_value = get_hand_value(dealer_hand)
        while dealer_hand_value < 17:
            dealer_hand.append(deck.pop())
            dealer_hand_value = get_hand_value(dealer_hand)
        result = await check_win(player_hand, dealer_hand, user.id, summ5, insurance)
        with suppress(TelegramBadRequest):
            await message.reply(result,

                                disable_web_page_preview=True)
            await state.clear()
        return
    if action == 'удвоить':
        if user.balance < summ5 * 2 + insurance:
            text_player = f'➖ 1-я рука:\n{await get_numerate_cards(player_hand)}'
            text_dil = f'{await get_numerate_cards(dealer_hand)}'
            with suppress(TelegramBadRequest):
                return await message.reply(
                    f"{rsmile} {user.link},Для удвоения требуется({to_str(summ5 * 2)}) + Cтраховка:"
                    f"\n🎫 Ваша рука: {get_hand_value(player_hand)}\n"
                    f"{text_player}"

                    f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                    f"\n {text_dil}"
                    ,

                    disable_web_page_preview=True)
            return
        player_hand.append(deck.pop())
        dealer_hand_value = get_hand_value(dealer_hand)
        while dealer_hand_value < 17:
            dealer_hand.append(deck.pop())
            dealer_hand_value = get_hand_value(dealer_hand)
        with suppress(TelegramBadRequest):
            result = await check_win(player_hand, dealer_hand, user.id, summ5 * 2, insurance)
            await message.reply(result,
                                disable_web_page_preview=True)

        return await state.clear()


@router.message(Trigger(["блэкджек", "бд"]))
async def start_blackjack(message: Message, state: FSMContext, bot: Bot, fsm_storage: BaseStorage):
    flood2 = await flood_handler2(message)
    flood = await flood_handler(message)
    if flood and flood2:
        state_get = await fsm_storage.get_state(bot=bot, key=StorageKey(
            user_id=message.from_user.id,
            chat_id=message.from_user.id,
            bot_id=bot.id))
        if state_get == 'BlackjackGame:waiting_for_action':
            return await check_state2(message, state, fsm_storage, bot)
        if state_get == 'BlackjackGame:waiting_for_action2':
            return await check_state2(message, state, fsm_storage, bot)
        if state_get == 'BlackjackGame:waiting_for_action3':
            return await check_state2(message, state, fsm_storage, bot)
        arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[
            0].lower() else message.text.split()[2:]
        user = User(user=message.from_user)
        try:
            summ5 = get_cash(arg[0] if arg[0].lower() not in ['всё', 'все'] else str(user.balance))
        except:
            summ5 = 0
        smile = ['♠', '🃏', '♣', '♥', '♦', '🎴']
        rsmile = random.choice(smile)
        if len(arg) == 0:
            return await message.answer(
                f"{rsmile} для начала игры в «БлэкДжек», введите сумму ставки: «Бд [сумма]» (минимальная ставка: 10$) "
                f"\n❓ Помощь: «Помощь блэкджек»")
        if summ5 <= 10:
            return await message.reply('❌ Ставка должна быть больше 10$',
                                       reply_markup=show_balance_kb.as_markup())
        if user.balance < summ5:
            return await message.reply('❌ Ошибка. Недостаточно денег на руках для ставки! 💸',
                                       reply_markup=show_balance_kb.as_markup())

        game_id = str(uuid4())
        newgame_dict = {"game_id": game_id}
        await fsm_storage.set_data(bot=bot, data=newgame_dict, key=StorageKey(
            user_id=message.from_user.id,
            chat_id=message.from_user.id,
            bot_id=bot.id))
        deck = create_deck()
        player_hand = [deck.pop(), deck.pop()]
        dealer_hand = [deck.pop()]
        player_hand2 = []

        if get_hand_value(player_hand) == 21:
            ssumm = summ5
            summ = int(summ5 * 2.5)

            with suppress(TelegramBadRequest):
                await message.reply(f"{rsmile} {user.link},БЛЭКДЖЭК! Вы выиграли!:"
                                    f"\n🎫 Ваша рука: {get_hand_value(player_hand)}"
                                    f"\n➖ 1-я рука:"
                                    f"\n 1️⃣ {player_hand[0]}"
                                    f"\n 2️⃣ {player_hand[1]}"
                                    f"\n🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                                    f"\n 1️⃣ {dealer_hand[0]}\n"
                                    f"получили +{to_str(summ - ssumm)} на баланс!",
                                    disable_web_page_preview=True)
                user.edit('balance', user.balance + summ - ssumm)
                return await state.clear()

        else:

            with suppress(TelegramBadRequest):
                await message.reply(f"{rsmile} {user.link},Новая игра началась!"
                                    f"\n🎫 Ваша рука: {get_hand_value(player_hand)}"
                                    f"\n➖ 1-я рука:"
                                    f"\n 1️⃣ {player_hand[0]}"
                                    f"\n 2️⃣ {player_hand[1]}"
                                    f"\n🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                                    f"\n 1️⃣ {dealer_hand[0]}"
                                    , disable_web_page_preview=True)
        await fsm_storage.set_state(bot=bot, state=BlackjackGame.waiting_for_action, key=StorageKey(
            user_id=message.from_user.id,
            chat_id=message.from_user.id,
            bot_id=bot.id))
        newgamedata_dict = {"deck": deck, 'player_hand': player_hand, 'player_hand2': player_hand2,
                            'dealer_hand': dealer_hand, 'summ': summ5, 'user_id': user.id}
        await fsm_storage.update_data(bot=bot, data=newgamedata_dict, key=StorageKey(
            user_id=message.from_user.id,
            chat_id=message.from_user.id,
            bot_id=bot.id))
