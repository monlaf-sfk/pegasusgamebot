import asyncio

from aiogram import flags
from aiogram.types import Message
from filters.users import flood_handler2, flood_handler
from config import bot_name
from keyboard.games import play_spin_kb
from keyboard.generate import show_balance_kb
from utils.main.cash import to_str, get_cash
from utils.main.users import User

from typing import List, Tuple

from utils.quests.main import QuestUser


def get_score_change(dice_value: int) -> int:
    """
    Проверка на выигрышную комбинацию
    :param dice_value: значение дайса (число)
    :return: изменение счёта игрока (число)
    """
    # Совпадающие значения (кроме 777)
    if dice_value in (1, 22, 43):
        return 3
    # Начинающиеся с двух семёрок (опять же, не учитываем 64)
    elif dice_value in (16, 32, 48, 61, 62, 63):
        return 2
    # Начинающиеся с двух лимонов (опять же, не учитываем 43)
    elif dice_value in (59, 27, 11, 41, 42, 44):
        return 1
    # Начинающиеся с двух бар (опять же, не учитываем 1)
    elif dice_value in (17, 33, 49, 2, 3, 4):
        return 1
    # Начинающиеся с двух виноград (опять же, не учитываем 22)
    elif dice_value in (38, 6, 54, 23, 24, 21):
        return 1
    # Джекпот (три семёрки)
    elif dice_value == 64:
        return 4
    else:
        return -1


def get_combo_text(dice_value: int) -> List[str]:
    """
    Возвращает то, что было на конкретном дайсе-спин
    :param dice_value: значение дайса (число)
    :return: массив строк, содержащий все выпавшие элементы в виде текста
    Альтернативный вариант (ещё раз спасибо t.me/svinerus):
        return [casino[(dice_value - 1) // i % 4]for i in (1, 4, 16)]
    """
    #           0       1         2        3
    values = ["BAR", "🍇", "🍋", "7️⃣"]

    dice_value -= 1
    result = []
    for _ in range(3):
        result.append(values[dice_value % 4])
        dice_value //= 4
    return result


def get_combo_data(dice_value: int) -> Tuple[int, str]:
    """
    Возвращает все необходимые для показа информации о комбинации данные
    :param dice_value: значение дайса (число)
    :return: Пара ("изменение счёта", "список выпавших элементов")
    """
    return (
        get_score_change(dice_value),
        ', '.join(get_combo_text(dice_value))
    )


multiplier_dict = {
    1: 1.5,
    2: 2,
    3: 2.5,
    4: 3
}


@flags.throttling_key('default')
async def spin_handler(message: Message):
    flood2 = await flood_handler2(message)
    flood = await flood_handler(message)
    if flood and flood2:

        arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[
            0].lower() else message.text.split()[2:]
        user = User(user=message.from_user)
        if len(arg) == 0:
            return await message.reply(f'🎰 {user.link}, для игры в Спин введите «Спин [ставка]» 👍🏼 \n'
                                       '💡 Сумму ставки можно указывать с помощью сокращений (например «1к» - ставка на 1000), либо словами «все» (ставка на весь баланс)'
                                       , disable_web_page_preview=True,
                                       reply_markup=play_spin_kb.as_markup())

        try:
            summ = ssumm = get_cash(arg[0] if arg[0].lower() not in ['всё', 'все'] else str(user.balance))
        except:
            summ = ssumm = 0
        if summ <= 0:
            return await message.reply(f'❌ {user.link}, Ставка меньше или равна нулю', disable_web_page_preview=True)

        if user.balance < summ:
            return await message.reply(f'❌ {user.link}, Недостаточно денег на руках для ставки! 💸',
                                       disable_web_page_preview=True,
                                       reply_markup=show_balance_kb.as_markup())

        casino = (await message.reply_dice(emoji='🎰')).dice
        score_change, combo_text = get_combo_data(casino.value)

        if score_change < 0:
            user.edit('balance', user.balance - summ)
            await asyncio.sleep(2.5)
            return await message.reply(
                f'😖 {user.link}, Ваша ставка была умножена на (x0) и вы потеряли {to_str(summ)}!\n'
                f'🎰 Комбинация: {str(combo_text).replace(",", " ")}', disable_web_page_preview=True,
                reply_markup=play_spin_kb.as_markup())

        if score_change in multiplier_dict:
            multiplier = multiplier_dict[score_change]
            summ = int(summ * multiplier)
            user.edit('balance', user.balance + summ - ssumm)
            await asyncio.sleep(2.5)
            await message.reply(
                f'🎰 {user.link}, Вы умножили свою ставку на (x{multiplier}) и получили +{to_str(summ)} на баланс!\n'
                f'🎰 Комбинация: {str(combo_text).replace(",", " ")}',
                disable_web_page_preview=True,
                reply_markup=play_spin_kb.as_markup()

            )

            result = QuestUser(user_id=user.id).update_progres(quest_ids=2, add_to_progresses=1)
            if result != '':
                await message.reply(text=result.format(user=user.link), disable_web_page_preview=True)
