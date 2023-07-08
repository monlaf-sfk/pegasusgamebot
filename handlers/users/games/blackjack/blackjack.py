import random
from contextlib import suppress
from uuid import uuid4

from aiogram import Router, F
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey, BaseStorage

from aiogram.types import Message, CallbackQuery

# Define a CallbackData object to store data about the game state


# Define the card values and suits
from config import bot_name
from filters.triggers import Trigger
from filters.users import flood_handler, flood_handler2
from handlers.users.games.blackjack.help_func import get_hand_value, create_deck, get_numerate_cards, check_win, \
    check_result, numbers_emoji
from handlers.users.games.blackjack.state import GameBlackjackCallback, BlackjackGame, NewGameCallbackBlackjack, \
    newgame_black_kb, game_blackjack_kb, replay_game_black_kb, game_blackjacksplit_kb, get_card_value, \
    to_str3, game_blackjack_insurance_kb
from keyboard.generate import show_balance_kb
from keyboard.main import check_ls_kb
from loader import bot
from middlewares.check_active_game import CheckActiveGameBlackMiddleware

from utils.main.cash import get_cash, to_str
from utils.main.users import User

router = Router()
router.message.filter(F.chat.type.in_({"private"}))
router.message.middleware(CheckActiveGameBlackMiddleware())
router.callback_query.middleware(CheckActiveGameBlackMiddleware())


async def help_blackjack(message: Message):
    if message.from_user.id == message.chat.id:
        await message.answer("""
    ♣️ Суть игры «Блэкджек» (не путайте с игрой «21 очко») заключается в том, чтобы обыграть Вашего противника (бота), заполучив бóльшее количество очков, но не более 21.
    ➖ Доступные действия:
    ⠀➕ Ещё - взять случайную карту
    ⠀❌ Стоп - закончить игру и узнать результат (или перейти к следующей руке)
    ⠀💰 Удвоить - удвоить ставку, взять случайную карту и закончить игру (или перейти к следующей руке)
    ⠀↔️ Разделить - удвоить ставку и разделить Вашу колоду на две руки
    ⠀⠀ ➖ Доступно только при наличии двух одинаковых по достоинству карт (2 и 2, король и дама и т.д)
    
    
    ➖ Возможные исходы:
    ⠀♣️ Блэкджек - 21 очко в начале игры, приз x2.5
    ⠀✅ Победа - приз x2 
    ⠀❌ Проигрыш - ставка аннулируется
    ⠀💸 Ничья - ставка возвращается 
    
    ♠️ Количество очков за каждые карты:
    ⠀ ➖ Карты от двойки до десятки: 2-10 очков соответственно
    ⠀ ➖ Карты «картинки» (король, дама, валет): 10 очков
    ⠀ ➖ (❗️) Туз: 11 очков, НО если сумма текущих двух карт больше 10, то цена туза — 1 очко""")
    else:
        with suppress(TelegramForbiddenError):
            await bot.send_message(chat_id=message.from_user.id, text="""
    ♣️ Суть игры «Блэкджек» (не путайте с игрой «21 очко») заключается в том, чтобы обыграть Вашего противника (бота), заполучив бóльшее количество очков, но не более 21.
    ➖ Доступные действия:
    ⠀➕ Ещё - взять случайную карту
    ⠀❌ Стоп - закончить игру и узнать результат (или перейти к следующей руке)
    ⠀💰 Удвоить - удвоить ставку, взять случайную карту и закончить игру (или перейти к следующей руке)
    ⠀↔️ Разделить - удвоить ставку и разделить Вашу колоду на две руки
    ⠀⠀ ➖ Доступно только при наличии двух одинаковых по достоинству карт (2 и 2, король и дама и т.д)
     ❤️ Застраховать - внести дополнительную ставку равную половине основной и застраховать Вашу колоду
⠀⠀     ➖ Доступно только при наличии у бота туза
⠀⠀     ➖ Если у бота «Блэкджек», Вам возвращается Ваша ставка полностью
    
    ➖ Возможные исходы:
    ⠀♣️ Блэкджек - 21 очко в начале игры, приз x2.5
    ⠀✅ Победа - приз x2 
    ⠀❌ Проигрыш - ставка аннулируется
    ⠀💸 Ничья - ставка возвращается 
    
    ♠️ Количество очков за каждые карты:
    ⠀ ➖ Карты от двойки до десятки: 2-10 очков соответственно
    ⠀ ➖ Карты «картинки» (король, дама, валет): 10 очков
    ⠀ ➖ (❗️) Туз: 11 очков, НО если сумма текущих двух карт больше 10, то цена туза — 1 очко""")
            return await message.reply('♣️ Блэкджек-Инструция была отправлена в личку с ботом!',
                                       reply_markup=check_ls_kb.as_markup())

        return await message.reply('🙃 Вы никогда не писали боту в лс, я не могу отправить вам ♣️ Блэкджек-Инструцию',
                                   reply_markup=check_ls_kb.as_markup())


async def check_state(message: Message, state: FSMContext, fsm_storage: BaseStorage, bot: bot):
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
            game_id = user_data.get("game_id")
            player_hand = user_data.get("player_hand")
            player_hand2 = user_data.get("player_hand2")
            dealer_hand = user_data.get("dealer_hand")

            if player_hand2:
                text_player = f'➖ 1-я рука - (Текущая): \n{await get_numerate_cards(player_hand)}'
                text_player2 = f'➖ 2-я рука: \n{await get_numerate_cards(player_hand2)}'
                text_dil = f'{await get_numerate_cards(dealer_hand)}'

                await message.message.edit_text(
                    f"{rsmile} {user.link}, Нажмите на кнопки для продолжения:"
                    f"\n🎫 Ваша руки: {get_hand_value(player_hand)} & {get_hand_value(player_hand2)}\n"
                    f"{text_player}"
                    f"{text_player2}"
                    f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                    f"\n{text_dil}"
                    ,
                    reply_markup=game_blackjack_kb(game_id, user.id, split=True),
                    disable_web_page_preview=True)
                return
            else:
                kb = game_blackjack_kb(game_id, user.id, player_hand, dealer_hand) if get_card_value(
                    player_hand[0]) != get_card_value(
                    player_hand[1]) else game_blackjacksplit_kb(game_id, user.id, dealer_hand)

                text_player = f'➖ 1-я рука: \n{await get_numerate_cards(player_hand)}'
                text_dil = f'{await get_numerate_cards(dealer_hand)}'
                await message.message.edit_text(
                    f"{rsmile} {user.link}, Нажмите на кнопки для продолжения:"
                    f"\n🎫 Ваша руки: {get_hand_value(player_hand)}\n"
                    f"{text_player}"
                    f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                    f"\n{text_dil}"
                    ,
                    reply_markup=kb,
                    disable_web_page_preview=True)
                return
        if state_get == 'BlackjackGame:waiting_for_action2':
            user_data = await fsm_storage.get_data(bot=bot, key=StorageKey(
                user_id=message.from_user.id,
                chat_id=message.from_user.id,
                bot_id=bot.id))
            game_id = user_data.get("game_id")
            player_hand = user_data.get("player_hand")
            player_hand2 = user_data.get("player_hand2")
            dealer_hand = user_data.get("dealer_hand")

            if player_hand2:
                text_player = f'➖ 1-я рука: \n{await get_numerate_cards(player_hand)}'
                text_player2 = f'➖ 2-я рука - (Текущая): \n{await get_numerate_cards(player_hand2)}'
                text_dil = f'{await get_numerate_cards(dealer_hand)}'

                await message.message.edit_text(
                    f"{rsmile} {user.link}, Нажмите на кнопки для продолжения:"
                    f"\n🎫 Ваша руки: {get_hand_value(player_hand)} & {get_hand_value(player_hand2)}\n"
                    f"{text_player}"
                    f"{text_player2}"
                    f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                    f"\n{text_dil}"
                    ,
                    reply_markup=game_blackjack_kb(game_id, user.id, split=True),
                    disable_web_page_preview=True)
                return
            else:
                kb = game_blackjack_kb(game_id, user.id, player_hand, dealer_hand) if get_card_value(
                    player_hand[0]) != get_card_value(
                    player_hand[1]) else game_blackjacksplit_kb(game_id, user.id, dealer_hand)

                text_player = f'➖ 1-я рука: \n{await get_numerate_cards(player_hand)}'
                text_dil = f'{await get_numerate_cards(dealer_hand)}'
                await message.message.edit_text(
                    f"{user.link}, Нажмите на кнопки для продолжения:"
                    f"\n🎫 Ваша руки: {get_hand_value(player_hand)}\n"
                    f"{text_player}"
                    f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                    f"\n{text_dil}"
                    ,
                    reply_markup=kb,
                    disable_web_page_preview=True)
                return
        if state_get == 'BlackjackGame:waiting_for_action3':

            user_data = await fsm_storage.get_data(bot=bot, key=StorageKey(
                user_id=message.from_user.id,
                chat_id=message.from_user.id,
                bot_id=bot.id))
            game_id = user_data.get("game_id")
            player_hand = user_data.get("player_hand")
            dealer_hand = user_data.get("dealer_hand")
            text_player = '➖ 1-я рука:\n'
            for index, cards in enumerate(player_hand, start=1):
                emoji = ''.join(numbers_emoji[int(i)] for i in str(index))
                text_player += f'  {emoji} {cards}\n'
            with suppress(TelegramBadRequest):
                await message.message.edit_text(
                    f"{rsmile} {user.link}, Нажмите на кнопки для продолжения:"
                    f"\n🎫 Ваша руки: {get_hand_value(player_hand)}\n"
                    f"{text_player}"
                    f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                    f"\n 1️⃣ {dealer_hand[0]}"
                    ,
                    reply_markup=game_blackjack_insurance_kb(game_id, message.from_user.id),
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

        game_id = user_data.get("game_id")
        player_hand = user_data.get("player_hand")
        player_hand2 = user_data.get("player_hand2")
        dealer_hand = user_data.get("dealer_hand")

        if player_hand2:
            text_player = f'➖ 1-я рука - (Текущая): \n{await get_numerate_cards(player_hand)}'
            text_player2 = f'➖ 2-я рука: \n{await get_numerate_cards(player_hand2)}'
            text_dil = f'{await get_numerate_cards(dealer_hand)}'

            await message.reply(
                f"{rsmile} {user.link}, Нажмите на кнопки для продолжения:"
                f"\n🎫 Ваша руки: {get_hand_value(player_hand)} & {get_hand_value(player_hand2)}\n"
                f"{text_player}"
                f"{text_player2}"
                f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                f"\n{text_dil}"
                ,
                reply_markup=game_blackjack_kb(game_id, user.id, split=True),
                disable_web_page_preview=True)
            return
        else:
            kb = game_blackjack_kb(game_id, user.id, player_hand, dealer_hand) if get_card_value(
                player_hand[0]) != get_card_value(
                player_hand[1]) else game_blackjacksplit_kb(game_id, user.id, dealer_hand)

            text_player = f'➖ 1-я рука: \n{await get_numerate_cards(player_hand)}'

            text_dil = f'{await get_numerate_cards(dealer_hand)}'
            await message.reply(
                f"{rsmile} {user.link}, Нажмите на кнопки для продолжения:"
                f"\n🎫 Ваша руки: {get_hand_value(player_hand)}\n"
                f"{text_player}"
                f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                f"\n{text_dil}"
                ,
                reply_markup=kb,
                disable_web_page_preview=True)
            return
    if state_get == 'BlackjackGame:waiting_for_action2':
        user_data = await fsm_storage.get_data(bot=bot, key=StorageKey(
            user_id=message.from_user.id,
            chat_id=message.from_user.id,
            bot_id=bot.id))
        game_id = user_data.get("game_id")
        player_hand = user_data.get("player_hand")
        player_hand2 = user_data.get("player_hand2")
        dealer_hand = user_data.get("dealer_hand")

        if player_hand2:
            text_player = f'➖ 1-я рука: \n{await get_numerate_cards(player_hand)}'
            text_player2 = f'➖ 2-я рука - (Текущая): \n{await get_numerate_cards(player_hand2)}'
            text_dil = f'{await get_numerate_cards(dealer_hand)}'

            await message.reply(
                f"{rsmile} {user.link}, Нажмите на кнопки для продолжения:"
                f"\n🎫 Ваша руки: {get_hand_value(player_hand)} & {get_hand_value(player_hand2)}\n"
                f"{text_player}"
                f"{text_player2}"
                f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                f"\n{text_dil}"
                ,
                reply_markup=game_blackjack_kb(game_id, user.id, split=True),
                disable_web_page_preview=True)
            return
        else:
            kb = game_blackjack_kb(game_id, user.id, player_hand, dealer_hand) if get_card_value(
                player_hand[0]) != get_card_value(
                player_hand[1]) else game_blackjacksplit_kb(game_id, user.id, dealer_hand)

            text_player = f'➖ 1-я рука: \n{await get_numerate_cards(player_hand)}'
            text_dil = f'{await get_numerate_cards(dealer_hand)}'
            await message.reply(
                f"{rsmile} {user.link}, Нажмите на кнопки для продолжения:"
                f"\n🎫 Ваша руки: {get_hand_value(player_hand)}\n"
                f"{text_player}"
                f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                f"\n{text_dil}"
                ,
                reply_markup=kb,
                disable_web_page_preview=True)
            return
    if state_get == 'BlackjackGame:waiting_for_action3':
        user_data = await fsm_storage.get_data(bot=bot, key=StorageKey(
            user_id=message.from_user.id,
            chat_id=message.from_user.id,
            bot_id=bot.id))
        game_id = user_data.get("game_id")
        player_hand = user_data.get("player_hand")
        dealer_hand = user_data.get("dealer_hand")
        text_player = '➖ 1-я рука:\n'
        for index, cards in enumerate(player_hand, start=1):
            emoji = ''.join(numbers_emoji[int(i)] for i in str(index))
            text_player += f'  {emoji} {cards}\n'
        with suppress(TelegramBadRequest):
            await message.reply(
                f"{rsmile} {user.link}, Нажмите на кнопки для продолжения:"
                f"\n🎫 Ваша руки: {get_hand_value(player_hand)}\n"
                f"{text_player}"
                f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                f"\n 1️⃣ {dealer_hand[0]}"
                ,
                reply_markup=game_blackjack_insurance_kb(game_id, message.from_user.id),
                disable_web_page_preview=True)
        return


@router.message(Trigger(["блэкджек", "бд"]))
async def start_blackjack(message: Message, state: FSMContext, bot: bot, fsm_storage: BaseStorage):
    flood2 = await flood_handler2(message)
    flood = await flood_handler(message)
    if flood and flood2:
        state_get = await fsm_storage.get_state(bot=bot, key=StorageKey(
            user_id=message.from_user.id,
            chat_id=message.from_user.id,
            bot_id=bot.id))
        if state_get == 'BlackjackGame:waiting_for_action':
            return await check_state(message, state, fsm_storage, bot)
        if state_get == 'BlackjackGame:waiting_for_action2':
            return await check_state(message, state, fsm_storage, bot)
        if state_get == 'BlackjackGame:waiting_for_action3':
            return await check_state(message, state, fsm_storage, bot)
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
                f"\n❓ Помощь: «Помощь блэкджек»",
                reply_markup=newgame_black_kb(message.from_user.id, summ5))
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
                                    reply_markup=replay_game_black_kb(message.from_user.id,
                                                                      summ5), disable_web_page_preview=True)
                user.edit('balance', user.balance + summ - ssumm)
                return await state.clear()

        else:

            kb = game_blackjack_kb(game_id, message.from_user.id, player_hand, dealer_hand) if get_card_value(
                player_hand[0]) != get_card_value(
                player_hand[1]) else game_blackjacksplit_kb(game_id, message.from_user.id, dealer_hand)
            with suppress(TelegramBadRequest):
                await message.reply(f"{rsmile} {user.link},Новая игра началась!"
                                    f"\n🎫 Ваша рука: {get_hand_value(player_hand)}"
                                    f"\n➖ 1-я рука:"
                                    f"\n 1️⃣ {player_hand[0]}"
                                    f"\n 2️⃣ {player_hand[1]}"
                                    f"\n🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                                    f"\n 1️⃣ {dealer_hand[0]}"
                                    , reply_markup=kb, disable_web_page_preview=True)
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


@router.callback_query(NewGameCallbackBlackjack.filter(), flags={"need_check_game": False})
async def new_game_blackjack(callback_query: CallbackQuery, state: FSMContext, callback_data: NewGameCallbackBlackjack,
                             fsm_storage: BaseStorage):
    state_get = await fsm_storage.get_state(bot=bot, key=StorageKey(
        user_id=callback_query.from_user.id,
        chat_id=callback_query.from_user.id,
        bot_id=bot.id))
    if state_get == 'BlackjackGame:waiting_for_action':
        return await check_state(callback_query, state, fsm_storage, bot)
    if state_get == 'BlackjackGame:waiting_for_action2':
        return await check_state(callback_query, state, fsm_storage, bot)
    if state_get == 'BlackjackGame:waiting_for_action3':
        return await check_state(callback_query, state, fsm_storage, bot)

    deck = create_deck()
    player_hand = [deck.pop(), deck.pop()]
    dealer_hand = [deck.pop()]
    player_hand2 = []
    summ5 = callback_data.summ
    user = User(user=callback_query.from_user)
    if summ5 <= 10:
        return await callback_query.message.edit_text('❌ Ставка должна быть больше 10$',
                                                      reply_markup=show_balance_kb.as_markup())
    if user.balance < summ5:
        return await callback_query.message.edit_text('❌ Ошибка. Недостаточно денег на руках для ставки! 💸',
                                                      reply_markup=show_balance_kb.as_markup())
    smile = ['♠', '🃏', '♣', '♥', '♦', '🎴']
    rsmile = random.choice(smile)
    game_id = str(uuid4())
    newgame_dict = {"game_id": game_id}
    await fsm_storage.set_data(bot=bot, data=newgame_dict, key=StorageKey(
        user_id=callback_query.from_user.id,
        chat_id=callback_query.from_user.id,
        bot_id=bot.id))
    with suppress(TelegramBadRequest):
        await callback_query.message.delete_reply_markup()
    if get_hand_value(player_hand) == 21:
        ssumm = summ5
        summ = int(summ5 * 2.5)

        with suppress(TelegramBadRequest):
            await callback_query.message.edit_text(f"{rsmile} {user.link},БЛЭКДЖЭК! Вы выиграли!:"
                                                   f"\n🎫 Ваша рука: {get_hand_value(player_hand)}"
                                                   f"\n➖ 1-я рука:"
                                                   f"\n 1️⃣ {player_hand[0]}"
                                                   f"\n 2️⃣ {player_hand[1]}"
                                                   f"\n🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                                                   f"\n 1️⃣ {dealer_hand[0]}\n"
                                                   f"получили +{to_str(summ - ssumm)} на баланс!",
                                                   reply_markup=replay_game_black_kb(callback_query.from_user.id,
                                                                                     summ5),
                                                   disable_web_page_preview=True)
            user.edit('balance', user.balance + summ - ssumm)
            return await state.clear()
    else:

        kb = game_blackjack_kb(game_id, callback_query.from_user.id, player_hand, dealer_hand) if get_card_value(
            player_hand[0]) != get_card_value(
            player_hand[1]) else game_blackjacksplit_kb(game_id, callback_query.from_user.id, dealer_hand)
        with suppress(TelegramBadRequest):
            await callback_query.message.edit_text(f"{rsmile} {user.link},Новая игра началась!"
                                                   f"\n🎫 Ваша рука: {get_hand_value(player_hand)}"
                                                   f"\n➖ 1-я рука:"
                                                   f"\n 1️⃣ {player_hand[0]}"
                                                   f"\n 2️⃣ {player_hand[1]}"
                                                   f"\n🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                                                   f"\n 1️⃣ {dealer_hand[0]}"
                                                   , reply_markup=kb, disable_web_page_preview=True)

    await fsm_storage.set_state(bot=bot, state=BlackjackGame.waiting_for_action, key=StorageKey(
        user_id=callback_query.from_user.id,
        chat_id=callback_query.from_user.id,
        bot_id=bot.id))
    newgamedata_dict = {"deck": deck, 'player_hand': player_hand, 'player_hand2': player_hand2,
                        'dealer_hand': dealer_hand, 'summ': summ5, 'user_id': user.id}
    await fsm_storage.update_data(bot=bot, data=newgamedata_dict, key=StorageKey(
        user_id=callback_query.from_user.id,
        chat_id=callback_query.from_user.id,
        bot_id=bot.id))


@router.callback_query(GameBlackjackCallback.filter(), BlackjackGame.waiting_for_action,
                       flags={"need_check_game": True})
async def action_blackjack(callback_query: CallbackQuery, state: FSMContext, callback_data: GameBlackjackCallback,
                           fsm_storage: BaseStorage):
    data = await fsm_storage.get_data(bot=bot, key=StorageKey(
        user_id=callback_query.from_user.id,
        chat_id=callback_query.from_user.id,
        bot_id=bot.id))
    summ5 = data.get("summ")
    deck = data.get("deck")
    player_hand = data.get("player_hand")
    player_hand2 = data.get("player_hand2")
    dealer_hand = data.get("dealer_hand")
    game_id = data.get("game_id")
    action = callback_data.action
    user = User(user=callback_query.from_user)
    if user.balance < summ5:
        return await callback_query.answer('❌ Ошибка. Недостаточно денег на руках для ставки! 💸'
                                           f'💰Требуется: {to_str3(summ5)} ', show_alert=True)
    smile = ['♠', '🃏', '♣', '♥', '♦', '🎴']
    rsmile = random.choice(smile)
    if action == "split":
        if get_card_value(player_hand[0]) != get_card_value(player_hand[1]) or len(
                player_hand) != 2 or len(player_hand2) > 0:
            text_player = f'➖ 1-я рука: \n{await get_numerate_cards(player_hand)}'
            with suppress(TelegramBadRequest):
                await callback_query.message.edit_text(
                    f"{rsmile} {user.link}, разделять можно только пару одного достоинства 👍🏻:"
                    f"\n🎫 Ваша рука: {get_hand_value(player_hand)}"
                    f"\n{text_player}",
                    reply_markup=game_blackjack_kb(game_id, callback_query.from_user.id, player_hand, dealer_hand),
                    disable_web_page_preview=True)
            return
        if user.balance < summ5 * 2:
            text_player = f'➖ 1-я рука: \n{await get_numerate_cards(player_hand)}'
            text_dil = f'{await get_numerate_cards(dealer_hand)}'
            with suppress(TelegramBadRequest):
                await callback_query.message.edit_text(
                    f"{rsmile} {user.link},Для разделения требуется({to_str(summ5 * 2)}):"
                    f"\n🎫 Ваша рука: {get_hand_value(player_hand)}"
                    f"\n{text_player}"
                    f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                    f"\n{text_dil}"
                    ,
                    reply_markup=game_blackjacksplit_kb(game_id, callback_query.from_user.id, dealer_hand),
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
            await callback_query.message.edit_text(f"{rsmile} {user.link} , Ваши очки:"
                                                   f"\n🎫 Ваши руки: {get_hand_value(player_hand)} & {get_hand_value(player_hand2)}\n"
                                                   f"{text_player}"
                                                   f"{text_player2}"
                                                   f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                                                   f"\n {text_dil}"
                                                   , reply_markup=game_blackjack_kb(game_id,
                                                                                    callback_query.from_user.id,
                                                                                    split=True),
                                                   disable_web_page_preview=True)
            newgamedata_dict = {"deck": deck, 'player_hand': player_hand, 'player_hand2': player_hand2,
                                'dealer_hand': dealer_hand}

            await fsm_storage.update_data(bot=bot, data=newgamedata_dict, key=StorageKey(
                user_id=callback_query.from_user.id,
                chat_id=callback_query.from_user.id,
                bot_id=bot.id))
            await fsm_storage.set_state(bot=bot, state=BlackjackGame.waiting_for_action, key=StorageKey(
                user_id=callback_query.from_user.id,
                chat_id=callback_query.from_user.id,
                bot_id=bot.id))

        return
    if action == "hit":
        if player_hand2:

            player_hand_value2 = get_hand_value(player_hand2)
            text_player2 = f'➖ 2-я рука: \n{await get_numerate_cards(player_hand2)}'
            if user.balance < summ5 * 2:
                text_player = f'➖ 1-я рука - (Текущая): \n{await get_numerate_cards(player_hand)}'
                text_dil = f'{await get_numerate_cards(dealer_hand)}'

                with suppress(TelegramBadRequest):
                    await callback_query.message.edit_text(
                        f"{rsmile} {user.link},Для продолжения требуется({to_str(summ5 * 2)}):"
                        f"\n🎫 Ваша руки: {get_hand_value(player_hand)} & {player_hand_value2}\n"
                        f"{text_player}"
                        f"{text_player2}"
                        f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                        f"\n {text_dil}"
                        ,
                        reply_markup=game_blackjacksplit_kb(game_id, callback_query.from_user.id, dealer_hand),
                        disable_web_page_preview=True)
                return
            player_hand.append(deck.pop())
            player_hand_value = get_hand_value(player_hand)

            if player_hand_value > 21:
                text_player = f'➖ 1-я рука: \n{await get_numerate_cards(player_hand)}'
                text_player2 = f'➖ 2-я рука - (Текущая): \n{await get_numerate_cards(player_hand2)}'
                text_dil = f'{await get_numerate_cards(dealer_hand)}'
                with suppress(TelegramBadRequest):

                    await callback_query.message.edit_text(f"{rsmile} {user.link},Вы вытянули {player_hand[-1]}: "
                                                           f"\n🎫 Ваша рука: {player_hand_value} & {player_hand_value2}\n"
                                                           f"{text_player}"
                                                           f"{text_player2}"
                                                           f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                                                           f"\n {text_dil}"
                                                           ,
                                                           reply_markup=game_blackjack_kb(game_id,
                                                                                          callback_query.from_user.id,
                                                                                          split=True),
                                                           disable_web_page_preview=True)
                    newgamedata_dict = {"deck": deck, 'player_hand': player_hand, 'player_hand2': player_hand2,
                                        'dealer_hand': dealer_hand}
                    await fsm_storage.update_data(bot=bot, data=newgamedata_dict, key=StorageKey(
                        user_id=callback_query.from_user.id,
                        chat_id=callback_query.from_user.id,
                        bot_id=bot.id))
                    await fsm_storage.set_state(bot=bot, state=BlackjackGame.waiting_for_action2, key=StorageKey(
                        user_id=callback_query.from_user.id,
                        chat_id=callback_query.from_user.id,
                        bot_id=bot.id))

                return
            else:
                with suppress(TelegramBadRequest):
                    text_player = f'➖ 1-я рука - (Текущая): \n{await get_numerate_cards(player_hand)}'
                    text_player2 = f'➖ 2-я рука: \n{await get_numerate_cards(player_hand2)}'
                    text_dil = f'{await get_numerate_cards(dealer_hand)}'
                    await callback_query.message.edit_text(f"{rsmile} {user.link},Вы вытянули {player_hand[-1]}:"
                                                           f"\n🎫 Ваша рука: {player_hand_value} & {player_hand_value2}\n"
                                                           f"{text_player}"
                                                           f"{text_player2}"
                                                           f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                                                           f"\n{text_dil}"
                                                           , reply_markup=game_blackjack_kb(game_id,
                                                                                            callback_query.from_user.id,
                                                                                            split=True),
                                                           disable_web_page_preview=True)

                    newgamedata_dict = {"deck": deck, 'player_hand': player_hand, 'player_hand2': player_hand2,
                                        'dealer_hand': dealer_hand}
                    await fsm_storage.update_data(bot=bot, data=newgamedata_dict, key=StorageKey(
                        user_id=callback_query.from_user.id,
                        chat_id=callback_query.from_user.id,
                        bot_id=bot.id))
                    await fsm_storage.set_state(bot=bot, state=BlackjackGame.waiting_for_action, key=StorageKey(
                        user_id=callback_query.from_user.id,
                        chat_id=callback_query.from_user.id,
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

                await callback_query.message.edit_text(f"{rsmile} {user.link},Вы вытянули {player_hand[-1]}: "
                                                       f"\n🎫 Ваша рука: {player_hand_value}\n"
                                                       f"{text_player}"
                                                       f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                                                       f"\n 1️⃣ {dealer_hand[0]}"
                                                       f"\nПровал! Вы проиграли!\n"
                                                       f"вы потеряли {to_str(summ5)}!",
                                                       reply_markup=replay_game_black_kb(callback_query.from_user.id,
                                                                                         summ5),
                                                       disable_web_page_preview=True)
                user.edit('balance', user.balance - summ5)
                await state.clear()
            return
        else:
            with suppress(TelegramBadRequest):
                await callback_query.message.edit_text(f"{rsmile} {user.link},Вы вытянули {player_hand[-1]}:"
                                                       f"\n🎫 Ваша рука: {get_hand_value(player_hand)}\n"
                                                       f"{text_player}"
                                                       f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                                                       f"\n 1️⃣ {dealer_hand[0]}"
                                                       , reply_markup=game_blackjack_kb(game_id,
                                                                                        callback_query.from_user.id,
                                                                                        player_hand, dealer_hand),
                                                       disable_web_page_preview=True)
                newgamedata_dict = {"deck": deck, 'player_hand': player_hand,
                                    'dealer_hand': dealer_hand}
                await fsm_storage.update_data(bot=bot, data=newgamedata_dict, key=StorageKey(
                    user_id=callback_query.from_user.id,
                    chat_id=callback_query.from_user.id,
                    bot_id=bot.id))

            return

    if action == 'stand':
        if player_hand2:
            text_player = f'➖ 1-я рука:\n{await get_numerate_cards(player_hand)}'

            text_player2 = f'➖ 2-я рука:(текущая)\n{await get_numerate_cards(player_hand2)}'

            if user.balance < summ5 * 2:
                with suppress(TelegramBadRequest):
                    text_dil = f'{await get_numerate_cards(dealer_hand)}'
                    await callback_query.message.edit_text(
                        f"{rsmile} {user.link},Для продолжения требуется({to_str(summ5 * 2)}):"
                        f"\n🎫 Ваша руки: {get_hand_value(player_hand)} & {get_hand_value(player_hand2)}\n"
                        f"{text_player}"
                        f"{text_player2}"
                        f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                        f"\n {text_dil}"
                        ,
                        reply_markup=game_blackjacksplit_kb(game_id, callback_query.from_user.id, dealer_hand),
                        disable_web_page_preview=True)
                return
            with suppress(TelegramBadRequest):
                text_dil = f'{await get_numerate_cards(dealer_hand)}'
                await callback_query.message.edit_text(f"{rsmile} {user.link}:"
                                                       f"\n🎫 Ваша руки: {get_hand_value(player_hand)} & {get_hand_value(player_hand2)}\n"
                                                       f"{text_player}"
                                                       f"{text_player2}"
                                                       f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                                                       f"\n {text_dil}"
                                                       , reply_markup=game_blackjack_kb(game_id,
                                                                                        callback_query.from_user.id,
                                                                                        split=True),
                                                       disable_web_page_preview=True)
                newgamedata_dict = {"deck": deck, 'player_hand': player_hand, 'player_hand2': player_hand2,
                                    'dealer_hand': dealer_hand}
                await fsm_storage.update_data(bot=bot, data=newgamedata_dict, key=StorageKey(
                    user_id=callback_query.from_user.id,
                    chat_id=callback_query.from_user.id,
                    bot_id=bot.id))

                await fsm_storage.set_state(bot=bot, state=BlackjackGame.waiting_for_action2, key=StorageKey(
                    user_id=callback_query.from_user.id,
                    chat_id=callback_query.from_user.id,
                    bot_id=bot.id))
            return
        dealer_hand_value = get_hand_value(dealer_hand)
        while dealer_hand_value < 17:
            dealer_hand.append(deck.pop())
            dealer_hand_value = get_hand_value(dealer_hand)
        result = await check_win(player_hand, dealer_hand, user.id, summ5)
        with suppress(TelegramBadRequest):
            await callback_query.message.edit_text(result,
                                                   reply_markup=replay_game_black_kb(callback_query.from_user.id,
                                                                                     summ5),
                                                   disable_web_page_preview=True)

        return await state.clear()
    if action == 'double':
        text_player = f'➖ 1-я рука:\n{await get_numerate_cards(player_hand)}'
        text_dil = f'{await get_numerate_cards(dealer_hand)}'
        if len(player_hand) != 2:
            with suppress(TelegramBadRequest):
                await callback_query.message.edit_text(
                    f"{rsmile} {user.link}, Удвоить можно только в начале игры:"
                    f"\n🎫 Ваша рука: {get_hand_value(player_hand)}"
                    f"\n{text_player}"
                    f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                    f"\n{text_dil}",
                    reply_markup=game_blackjack_kb(game_id, callback_query.from_user.id, player_hand, dealer_hand)
                    , disable_web_page_preview=True)
            return
        if user.balance < summ5 * 2:
            with suppress(TelegramBadRequest):
                return await callback_query.message.edit_text(
                    f"{rsmile} {user.link},Для удвоения требуется({to_str(summ5 * 2)}):"
                    f"\n🎫 Ваша рука: {get_hand_value(player_hand)}\n"
                    f"{text_player}"

                    f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                    f"\n {text_dil}"
                    ,
                    reply_markup=game_blackjack_kb(game_id, callback_query.from_user.id, player_hand, dealer_hand),
                    disable_web_page_preview=True)
            return
        player_hand.append(deck.pop())
        dealer_hand_value = get_hand_value(dealer_hand)
        while dealer_hand_value < 17:
            dealer_hand.append(deck.pop())
            dealer_hand_value = get_hand_value(dealer_hand)
        with suppress(TelegramBadRequest):
            result = await check_win(player_hand, dealer_hand, user.id, summ5 * 2)
            await callback_query.message.edit_text(result,
                                                   reply_markup=replay_game_black_kb(callback_query.from_user.id,
                                                                                     summ5),
                                                   disable_web_page_preview=True)

        return await state.clear()

    if action == 'surrender':
        text_player = f'➖ 1-я рука:\n{await get_numerate_cards(player_hand)}'
        text_dil = f'{await get_numerate_cards(dealer_hand)}'
        if len(player_hand) != 2:
            with suppress(TelegramBadRequest):
                await callback_query.message.edit_text(
                    f"{rsmile} {user.link}, Отказаться можно только в начале игры:"
                    f"\n🎫 Ваша рука: {get_hand_value(player_hand)}"
                    f"\n{text_player}"
                    f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                    f"\n{text_dil}"
                    , reply_markup=game_blackjack_kb(game_id, callback_query.from_user.id, player_hand, dealer_hand),
                    disable_web_page_preview=True)
            return
        user.edit('balance', user.balance - round(summ5 / 2))
        with suppress(TelegramBadRequest):
            await callback_query.message.edit_text(
                f"{rsmile} {user.link}:"
                f"\n🎫 Ваша рука: {get_hand_value(player_hand)}\n"
                f"{text_player}"
                f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                f"\n {text_dil}"
                f"\n\n🚫 Вы отказались от игры и потеряли половину своей суммы!"
                ,
                reply_markup=replay_game_black_kb(callback_query.from_user.id,
                                                  summ5),
                disable_web_page_preview=True)

        return await state.clear()
    if action == 'insurance':
        text_player = f'➖ 1-я рука: \n{await get_numerate_cards(player_hand)}'
        text_dil = f'{await get_numerate_cards(dealer_hand)}'
        if dealer_hand and get_card_value(dealer_hand[0]) != 11 and len(player_hand) == 2:
            with suppress(TelegramBadRequest):
                await callback_query.message.edit_text(
                    f"{rsmile} {user.link}, Доступно только при наличии у бота туза :"
                    f"\n🎫 Ваша рука: {get_hand_value(player_hand)}"
                    f"\n{text_player}"
                    f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                    f"\n{text_dil}"

                    , reply_markup=game_blackjack_kb(game_id, callback_query.from_user.id, player_hand, dealer_hand),
                    disable_web_page_preview=True)
            return
        if user.balance < (round(summ5 / 2)) + summ5:
            with suppress(TelegramBadRequest):
                await callback_query.message.edit_text(
                    f"{rsmile} {user.link}, для страхования дополнительно требуется ({to_str(round(summ5 / 2))}):"
                    f"\n🎫 Ваша рука: {get_hand_value(player_hand)}"
                    f"\n{text_player}"
                    f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                    f"\n{text_dil}"
                    ,
                    reply_markup=game_blackjack_kb(game_id, callback_query.from_user.id, player_hand, dealer_hand),
                    disable_web_page_preview=True)
            return
        with suppress(TelegramBadRequest):
            text_player = f'➖ 1-я рука:\n{await get_numerate_cards(player_hand)}'
            text_dil = f'{await get_numerate_cards(dealer_hand)}'
            await callback_query.message.edit_text(
                f"{rsmile} {user.link}:"
                f"\n🎫 Ваша рука: {get_hand_value(player_hand)}\n"
                f"{text_player}"
                f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                f"\n {text_dil}"
                f"\n\nВы застраховали свою ставку за {to_str(round(summ5 / 2))} 👍🏼!"
                ,
                reply_markup=game_blackjack_insurance_kb(game_id, callback_query.from_user.id),
                disable_web_page_preview=True)
        newgamedata_dict = {"deck": deck, 'player_hand': player_hand,
                            'dealer_hand': dealer_hand, 'insurance': round(summ5 / 2)}
        await fsm_storage.update_data(bot=bot, data=newgamedata_dict, key=StorageKey(
            user_id=callback_query.from_user.id,
            chat_id=callback_query.from_user.id,
            bot_id=bot.id))
        await fsm_storage.set_state(bot=bot, state=BlackjackGame.waiting_for_action3, key=StorageKey(
            user_id=callback_query.from_user.id,
            chat_id=callback_query.from_user.id,
            bot_id=bot.id))


@router.callback_query(GameBlackjackCallback.filter(), BlackjackGame.waiting_for_action2,
                       flags={"need_check_game": True})
async def action2_blackjack(callback_query: CallbackQuery, state: FSMContext, callback_data: GameBlackjackCallback,
                            fsm_storage: BaseStorage):
    data = await fsm_storage.get_data(bot=bot, key=StorageKey(
        user_id=callback_query.from_user.id,
        chat_id=callback_query.from_user.id,
        bot_id=bot.id))
    summ5 = data.get("summ")
    deck = data.get("deck")
    game_id = data.get("game_id")
    player_hand = data.get("player_hand")
    dealer_hand = data.get("dealer_hand")
    player_hand2 = data.get("player_hand2")
    action = callback_data.action
    user = User(user=callback_query.from_user)
    if user.balance < summ5 * 2:
        return await callback_query.answer('❌ Ошибка. Недостаточно денег на руках для ставки! 💸'
                                           f'💰Требуется: {to_str3(summ5 * 2)} ', show_alert=True)
    smile = ['♠', '🃏', '♣', '♥', '♦', '🎴']
    rsmile = random.choice(smile)
    if action == "hit":
        player_hand2.append(deck.pop())
        player_hand_value2 = get_hand_value(player_hand2)
        text_player2 = f'➖ 2-я рука:(текущая)\n{await get_numerate_cards(player_hand2)}'

        if user.balance < summ5 * 2:
            text_diller = f'{await get_numerate_cards(dealer_hand)}'
            text_player = f'➖ 1-я рука:\n{await get_numerate_cards(player_hand)}'
            with suppress(TelegramBadRequest):
                await callback_query.message.edit_text(
                    f"{rsmile} {user.link},Для продолжения требуется({to_str(summ5 * 2)}):"
                    f"\n🎫 Ваша руки: {get_hand_value(player_hand)} & {player_hand_value2}\n"
                    f"{text_player}"
                    f"{text_player2}"
                    f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                    f"\n{text_diller} "
                    ,
                    reply_markup=game_blackjacksplit_kb(game_id, callback_query.from_user.id, dealer_hand),
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
                await callback_query.message.edit_text(result,
                                                       reply_markup=replay_game_black_kb(callback_query.from_user.id,
                                                                                         summ5),
                                                       disable_web_page_preview=True)

                await state.clear()
            return

        else:
            with suppress(TelegramBadRequest):
                await callback_query.message.edit_text(f"{rsmile} {user.link},Вы вытянули {player_hand[-1]}:"
                                                       f"\n🎫 Ваша рука: {get_hand_value(player_hand)} & {get_hand_value(player_hand2)}\n"
                                                       f"{text_player}"
                                                       f"{text_player2}"
                                                       f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                                                       f"\n 1️⃣ {dealer_hand[0]}"
                                                       , reply_markup=game_blackjack_kb(game_id,
                                                                                        callback_query.from_user.id,
                                                                                        split=True),
                                                       disable_web_page_preview=True)

                newgamedata_dict = {"deck": deck, 'player_hand': player_hand, 'player_hand2': player_hand2,
                                    'dealer_hand': dealer_hand}
                await fsm_storage.update_data(bot=bot, data=newgamedata_dict, key=StorageKey(
                    user_id=callback_query.from_user.id,
                    chat_id=callback_query.from_user.id,
                    bot_id=bot.id))
                await fsm_storage.set_state(bot=bot, state=BlackjackGame.waiting_for_action2, key=StorageKey(
                    user_id=callback_query.from_user.id,
                    chat_id=callback_query.from_user.id,
                    bot_id=bot.id))

        return
    if action == 'stand':
        dealer_hand_value = get_hand_value(dealer_hand)
        while dealer_hand_value < 17:
            dealer_hand.append(deck.pop())
            dealer_hand_value = get_hand_value(dealer_hand)
        result = await check_result(player_hand, player_hand2, dealer_hand, user.id, summ5)
        with suppress(TelegramBadRequest):
            await callback_query.message.edit_text(result,
                                                   reply_markup=replay_game_black_kb(callback_query.from_user.id,
                                                                                     summ5),
                                                   disable_web_page_preview=True)
            await state.clear()
        return


@router.callback_query(GameBlackjackCallback.filter(), BlackjackGame.waiting_for_action3,
                       flags={"need_check_game": True})
async def action3_blackjack(callback_query: CallbackQuery, state: FSMContext, callback_data: GameBlackjackCallback,
                            fsm_storage: BaseStorage):
    data = await fsm_storage.get_data(bot=bot, key=StorageKey(
        user_id=callback_query.from_user.id,
        chat_id=callback_query.from_user.id,
        bot_id=bot.id))
    insurance = data.get("insurance")
    summ5 = data.get("summ")
    deck = data.get("deck")
    game_id = data.get("game_id")
    player_hand = data.get("player_hand")
    dealer_hand = data.get("dealer_hand")
    action = callback_data.action
    user = User(user=callback_query.from_user)
    if user.balance < summ5 + insurance:
        return await callback_query.answer('❌ Ошибка. Недостаточно денег на руках для ставки! 💸'
                                           f'💰Требуется: {to_str3(summ5 + insurance)} ', show_alert=True)
    smile = ['♠', '🃏', '♣', '♥', '♦', '🎴']
    rsmile = random.choice(smile)
    if action == "hit":
        player_hand.append(deck.pop())
        player_hand_value = get_hand_value(player_hand)
        text_player = '➖ 1-я рука:\n'
        for index, cards in enumerate(player_hand, start=1):
            emoji = ''.join(numbers_emoji[int(i)] for i in str(index))
            text_player += f'  {emoji} {cards}\n'
        if player_hand_value > 21:
            with suppress(TelegramBadRequest):

                await callback_query.message.edit_text(f"{rsmile} {user.link},Вы вытянули {player_hand[-1]}: "
                                                       f"\n🎫 Ваша рука: {player_hand_value}\n"
                                                       f"{text_player}"
                                                       f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                                                       f"\n 1️⃣ {dealer_hand[0]}"
                                                       f"\nПровал! Вы проиграли!\n"
                                                       f"вы потеряли {to_str(summ5)}!",
                                                       reply_markup=replay_game_black_kb(callback_query.from_user.id,
                                                                                         summ5),
                                                       disable_web_page_preview=True)
                user.edit('balance', user.balance - summ5 + insurance)
                await state.clear()
            return
        else:
            with suppress(TelegramBadRequest):
                await callback_query.message.edit_text(f"{rsmile} {user.link},Вы вытянули {player_hand[-1]}:"
                                                       f"\n🎫 Ваша рука: {get_hand_value(player_hand)}\n"
                                                       f"{text_player}"
                                                       f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                                                       f"\n 1️⃣ {dealer_hand[0]}"
                                                       , reply_markup=game_blackjack_kb(game_id,
                                                                                        callback_query.from_user.id,
                                                                                        player_hand, dealer_hand),
                                                       disable_web_page_preview=True)
                newgamedata_dict = {"deck": deck, 'player_hand': player_hand,
                                    'dealer_hand': dealer_hand}
                await fsm_storage.update_data(bot=bot, data=newgamedata_dict, key=StorageKey(
                    user_id=callback_query.from_user.id,
                    chat_id=callback_query.from_user.id,
                    bot_id=bot.id))
                await fsm_storage.set_state(bot=bot, state=BlackjackGame.waiting_for_action3, key=StorageKey(
                    user_id=callback_query.from_user.id,
                    chat_id=callback_query.from_user.id,
                    bot_id=bot.id))
            return
    if action == 'stand':
        dealer_hand_value = get_hand_value(dealer_hand)
        while dealer_hand_value < 17:
            dealer_hand.append(deck.pop())
            dealer_hand_value = get_hand_value(dealer_hand)
        result = await check_win(player_hand, dealer_hand, user.id, summ5, insurance)
        with suppress(TelegramBadRequest):
            await callback_query.message.edit_text(result,
                                                   reply_markup=replay_game_black_kb(callback_query.from_user.id,
                                                                                     summ5),
                                                   disable_web_page_preview=True)
            await state.clear()
        return
    if action == 'double':
        if user.balance < summ5 * 2 + insurance:
            text_player = f'➖ 1-я рука:\n{await get_numerate_cards(player_hand)}'
            text_dil = f'{await get_numerate_cards(dealer_hand)}'
            with suppress(TelegramBadRequest):
                return await callback_query.message.edit_text(
                    f"{rsmile} {user.link},Для удвоения требуется({to_str(summ5 * 2)}) + Cтраховка:"
                    f"\n🎫 Ваша рука: {get_hand_value(player_hand)}\n"
                    f"{text_player}"

                    f"🎟 Рука дилера: {get_hand_value(dealer_hand)}"
                    f"\n {text_dil}"
                    ,
                    reply_markup=game_blackjack_kb(game_id, callback_query.from_user.id, player_hand, dealer_hand),
                    disable_web_page_preview=True)
            return
        player_hand.append(deck.pop())
        dealer_hand_value = get_hand_value(dealer_hand)
        while dealer_hand_value < 17:
            dealer_hand.append(deck.pop())
            dealer_hand_value = get_hand_value(dealer_hand)
        with suppress(TelegramBadRequest):
            result = await check_win(player_hand, dealer_hand, user.id, summ5 * 2, insurance)
            await callback_query.message.edit_text(result,
                                                   reply_markup=replay_game_black_kb(callback_query.from_user.id,
                                                                                     summ5),
                                                   disable_web_page_preview=True)

        return await state.clear()
