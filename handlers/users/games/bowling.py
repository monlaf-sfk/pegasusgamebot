import asyncio

from aiogram import flags
from aiogram.types import Message
from filters.users import flood_handler2, flood_handler
from config import bot_name
from keyboard.games import play_bowling_kb
from keyboard.generate import show_balance_kb
from utils.main.cash import to_str, get_cash

from utils.main.users import User

values = {
    2: [1, 2, 3],
    3: [4]
}


@flags.throttling_key('default')
async def bowling_handler(message: Message):
    flood2 = await flood_handler2(message)
    flood = await flood_handler(message)
    if flood and flood2:
        arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[
            0].lower() else message.text.split()[2:]
        user = User(user=message.from_user)
        if len(arg) == 0:
            return await message.reply(f'🎳 {user.link}, для игры в боулинг введите «Боулинг [ставка]» 👍🏼 \n'
                                       '💡 Сумму ставки можно указывать с помощью сокращений (например «1к» - ставка на 1000), либо словами «все» (ставка на весь баланс)'
                                       , disable_web_page_preview=True,
                                       reply_markup=play_bowling_kb.as_markup())

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

        bowling = (await message.reply_dice(emoji='🎳')).dice

        if bowling.value in values[3]:
            await asyncio.sleep(3)
            return await message.reply(
                f'🎳 {user.link}, Вы сохранили свои средства! (х1)',
                disable_web_page_preview=True,
                reply_markup=play_bowling_kb.as_markup())
        elif bowling.value == 5:
            summ = int(summ * 1.25)
            user.edit('balance', user.balance + summ - ssumm)
            await asyncio.sleep(3)
            return await message.reply(
                f'🎳 {user.link},  Вы умножили свою ставку на (x1.25) и получили +{to_str(summ)} на баланс!',
                disable_web_page_preview=True,
                reply_markup=play_bowling_kb.as_markup())
        elif bowling.value == 6:
            summ = int(summ * 2.5)
            user.edit('balance', user.balance + summ - ssumm)
            await asyncio.sleep(3)
            return await message.reply(
                f'🎳 {user.link}, Вы умножили свою ставку на (x3) и получили +{to_str(summ)} на баланс!',
                disable_web_page_preview=True,
                reply_markup=play_bowling_kb.as_markup())
        else:
            user.edit('balance', user.balance - summ)
            await asyncio.sleep(3)
            return await message.reply(
                f'😖 {user.link}, Ваша ставка была умножена на (x0) и вы потеряли {to_str(summ)}!',
                disable_web_page_preview=True,
                reply_markup=play_bowling_kb.as_markup())
