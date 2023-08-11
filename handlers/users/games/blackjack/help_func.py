import random

from utils.main.cash import to_str
from utils.main.users import User
from utils.quests.main import QuestUser

card_values = ["Туз", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Валет", "Дама", "Кароль"]
card_suits = ["♥", "♦", "♣", "♠"]
numbers_emoji = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']


def get_card_value(card):
    value = card.split()[0]
    if value == "Туз":
        return 11
    elif value in ["Кароль", "Дама", "Валет", "10"]:
        return 10
    else:
        return int(value)


def get_hand_value(hand):
    total_value = 0
    num_aces = 0
    for card in hand:
        value = get_card_value(card)
        if value == 11:
            num_aces += 1
        total_value += value
    while total_value > 21 and num_aces > 0:
        total_value -= 10
        num_aces -= 1
    return total_value


async def get_numerate_cards(hand) -> str:
    text = ''
    for index, cards in enumerate(hand, start=1):
        emoji = ''.join(numbers_emoji[int(i)] for i in str(index))
        text += f'  {emoji} {cards}\n'
    return text


async def check_win(player_hand: list, dealer_hand: list, user_id: int, summ: int, insurance: int = None) -> str:
    user = User(id=user_id)
    player_hand_value = get_hand_value(player_hand)
    dealer_hand_value = get_hand_value(dealer_hand)
    smile = ['♠', '🃏', '♣', '♥', '♦', '🎴']
    rsmile = random.choice(smile)
    text = ''
    result = QuestUser(user_id=user.id).update_progres(quest_ids=3, add_to_progresses=1)
    if result != '':
        result = result.format(user=user.link)
    else:
        result = False
    if insurance:
        if dealer_hand_value == 21:
            text_player = f'➖ 1-я рука - Страховка спасла [♥]: \n{await  get_numerate_cards(player_hand)}'
            text_dil = f'{await  get_numerate_cards(dealer_hand)}'
            text = f"{rsmile} {user.link} ,Результаты:" \
                   f"\n🎫 Ваша рука: {player_hand_value}\n" \
                   f"{text_player}" \
                   f"\n🎟 Рука дилера: {dealer_hand_value}" \
                   f"\n{text_dil}"
            return text, result
        user.edit('balance', user.balance - insurance)
        text += "💔 Ваша страховка сгорела\n"
    if player_hand_value > 21:
        text_player = f'➖ 1-я рука - Поражение [❌]: \n{await get_numerate_cards(player_hand)}'
        text_dil = f'{await get_numerate_cards(dealer_hand)}'
        user.edit('balance', user.balance - summ)
        text += f"{rsmile} {user.link}, Результаты:" \
                f"\n🎫 Ваша рука: {player_hand_value}\n" \
                f"{text_player}" \
                f"\n🎟 Рука дилера: {dealer_hand_value}" \
                f"\n{text_dil}" \
                f"\n\nВы проиграли 🙁 ({to_str(summ)})"
        return text, result
    elif dealer_hand_value > 21:
        text_player = f'➖ 1-я рука - Победа [✔]: \n{await get_numerate_cards(player_hand)}'
        text_dil = f'{await get_numerate_cards(dealer_hand)}'
        user.edit('balance', user.balance + summ)
        text += f"{rsmile} {user.link}, Результаты:" \
                f"\n🎫 Ваша рука: {player_hand_value}\n" \
                f"{text_player}" \
                f"\n🎟 Рука дилера: {dealer_hand_value}" \
                f"\n{text_dil}" \
                f"\n\nПобеда! Ваш приз: {to_str(summ * 2)} [x2]"
        return text, result
    elif player_hand_value > dealer_hand_value:
        text_player = f'➖ 1-я рука - Победа [✔]: \n{await get_numerate_cards(player_hand)}'
        text_dil = f'{await  get_numerate_cards(dealer_hand)}'
        user.edit('balance', user.balance + summ)
        text += f"{rsmile} {user.link}, Результаты:" \
                f"\n🎫 Ваша рука: {player_hand_value}\n" \
                f"{text_player}" \
                f"\n🎟 Рука дилера: {dealer_hand_value}" \
                f"\n{text_dil}" \
                f"\n\nПобеда! Ваш приз: {to_str(summ * 2)} [x2]"
        return text, result
    elif dealer_hand_value > player_hand_value:
        text_player = f'➖ 1-я рука - Поражение [❌]: \n{await  get_numerate_cards(player_hand)}'
        text_dil = f'{await  get_numerate_cards(dealer_hand)}'
        user.edit('balance', user.balance - summ)
        text += f"{rsmile} {user.link}, Результаты:" \
                f"\n🎫 Ваша рука: {player_hand_value}\n" \
                f"{text_player}" \
                f"\n🎟 Рука дилера: {dealer_hand_value}" \
                f"\n{text_dil}" \
                f"\n\nВы проиграли 🙁 ({to_str(summ)})"
        return text, result
    else:
        text_player = f'➖ 1-я рука - Ничья [🟰]: \n{await  get_numerate_cards(player_hand)}'
        text_dil = f'{await  get_numerate_cards(dealer_hand)}'
        text += f"{rsmile} {user.link} ,Результаты:" \
                f"\n🎫 Ваша рука: {player_hand_value}\n" \
                f"{text_player}" \
                f"\n🎟 Рука дилера: {dealer_hand_value}" \
                f"\n{text_dil}"
        return text, result


async def check_result(player_hand, player_hand2, dealer_hand, user_id, summ):
    try:
        player_hand_value = get_hand_value(player_hand)
        player_hand_value2 = get_hand_value(player_hand2)
        dealer_hand_value = get_hand_value(dealer_hand)
    except ValueError:
        return "Error", "Error"
    smile = ['♠', '🃏', '♣', '♥', '♦', '🎴']
    rsmile = random.choice(smile)
    user = User(id=user_id)
    if player_hand_value > 21:
        text_player = f'➖ 1-я рука - Поражение [❌]: \n{await get_numerate_cards(player_hand)}\n Вы проиграли 🙁 ({to_str(summ)})\n'
        user.edit('balance', user.balance - summ)
    elif dealer_hand_value > 21:
        text_player = f'➖ 1-я рука - Победа [✔]: \n{await get_numerate_cards(player_hand)}\nПобеда! Ваш приз: {to_str(summ * 2)} [x2]\n'
        user.edit('balance', user.balance + summ)
    elif player_hand_value > dealer_hand_value:
        text_player = f'➖ 1-я рука - Победа [✔]: \n{await get_numerate_cards(player_hand)}\nПобеда! Ваш приз: {to_str(summ * 2)} [x2]\n'
        user.edit('balance', user.balance + summ)
    elif dealer_hand_value > player_hand_value:
        text_player = f'➖ 1-я рука - Поражение [❌]: \n{await  get_numerate_cards(player_hand)}\n Вы проиграли 🙁 ({to_str(summ)})\n'
        user.edit('balance', user.balance - summ)
    else:
        text_player = f'➖ 1-я рука - Ничья [🟰]: \n{await  get_numerate_cards(player_hand)}\n'

    if player_hand_value2 > 21:
        text_player2 = f'➖ 2-я рука - Поражение [❌]: \n{await get_numerate_cards(player_hand2)}\n Вы проиграли 🙁 ({to_str(summ)})\n'
        user.edit('balance', user.balance - summ)
    elif dealer_hand_value > 21:
        text_player2 = f'➖ 2-я рука - Победа [✔]: \n{await get_numerate_cards(player_hand2)}\nПобеда! Ваш приз: {to_str(summ * 2)} [x2]\n'
        user.edit('balance', user.balance + summ)
    elif player_hand_value2 > dealer_hand_value:
        text_player2 = f'➖ 2-я рука - Победа [✔]: \n{await get_numerate_cards(player_hand2)}\nПобеда! Ваш приз: {to_str(summ * 2)} [x2]\n'
        user.edit('balance', user.balance + summ)
    elif dealer_hand_value > player_hand_value2:
        text_player2 = f'➖ 2-я рука - Поражение [❌]: \n{await  get_numerate_cards(player_hand2)}\n Вы проиграли 🙁 ({to_str(summ)})\n'
        user.edit('balance', user.balance - summ)
    else:
        text_player2 = f'➖ 2-я рука - Ничья [🟰]: \n{await  get_numerate_cards(player_hand2)}\n'

    text_dil = f'{await  get_numerate_cards(dealer_hand)}'
    text = f"{rsmile} {user.link}, Результаты:" \
           f"\n🎫 Ваша рука: {player_hand_value} & {player_hand_value2}\n" \
           f"{text_player}" \
           f"{text_player2}" \
           f"\n🎟 Рука дилера: {dealer_hand_value}" \
           f"\n{text_dil}"
    result = QuestUser(user_id=user.id).update_progres(quest_ids=3, add_to_progresses=1)
    if result != '':
        return text, result.format(user=user.link)
    return text, False


def create_deck():
    deck = []
    for suit in card_suits:
        for value in card_values:
            deck.append(f"{value} {suit}")
    random.shuffle(deck)
    return deck
