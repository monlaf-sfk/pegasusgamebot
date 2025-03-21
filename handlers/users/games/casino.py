import random

import numpy as np
from aiogram import flags
from aiogram.types import Message

from config import bot_name
from filters.users import flood_handler2, flood_handler
from keyboard.games import play_casino_kb
from keyboard.generate import show_balance_kb

from utils.main.cash import get_cash, to_str
from utils.main.users import User


@flags.throttling_key('default')
async def casino_handler(message: Message):
    flood2 = await flood_handler2(message)
    flood = await flood_handler(message)
    if flood and flood2:
        user = User(user=message.from_user)
        arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[
            0].lower() else message.text.split()[2:]
        if len(arg) == 0:
            return await message.reply(f'{user.link}, для игры в казино введите «Казино [ставка]» 👍🏼 \n'
                                       '💡 Сумму ставки можно указывать с помощью сокращений (например «1к» - ставка на 1000), либо словами «все» (ставка на весь баланс)'
                                       , disable_web_page_preview=True,
                                       reply_markup=play_casino_kb.as_markup())
        win = ['🙂', '😋', '😄', '😃']
        loser = ['😔', '😕', '😣', '😞', '😢']
        smile = ['♠', '🃏', '♣', '♥', '♦', '🎴']
        rsmile = random.choice(smile)
        rwin = random.choice(win)
        rloser = random.choice(loser)

        balance_factor = min(float(user.balance + user.bank + user.deposit) / float(1_000_000_000),
                             1.0)  # Capped at 1.0

        # Calculate adjusted probabilities based on the balance factor
        base_probabilities = [0.1, 0.16, 0.2, 0.2, 0.1, 0.1, 0.1, 0.1, 0.1, 0.02]

        # Reverse the balance factor to make losses more likely for players with higher balances
        loss_factor = 1.0 - balance_factor

        # Adjust the probabilities based on the loss_factor while maintaining some randomness
        adjusted_probabilities = [
            (1 - loss_factor) * p + loss_factor * random.uniform(0.9, 1.1) / len(base_probabilities)
            for p in base_probabilities
        ]

        # Normalize the adjusted probabilities
        adjusted_probabilities = [p / sum(adjusted_probabilities) for p in adjusted_probabilities]
        # Generate the random outcome
        rx = np.random.choice(range(1, 11), 1, p=adjusted_probabilities)[0]

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

        if int(rx) == 1:
            await message.reply(
                f'{rsmile} {user.link}, вы проиграли {to_str(summ)}  x0 {rloser}',
                parse_mode='html', disable_web_page_preview=True, reply_markup=play_casino_kb.as_markup())
            user.edit('balance', user.balance - ssumm)
            return
        if int(rx) == 2:
            summ = int(summ * 0.25)
            user.edit('balance', user.balance - summ)
            return await message.reply(
                f'{rsmile} {user.link}, вы проиграли {to_str(summ)}  x0.25 {rloser}',
                parse_mode='html', disable_web_page_preview=True, reply_markup=play_casino_kb.as_markup())

        if int(rx) == 3:
            summ = int(summ * 0.5)
            user.edit('balance', user.balance - summ)
            await message.reply(
                f'{rsmile} {user.link}, вы проиграли {to_str(summ)}  x0.5 {rloser}',
                parse_mode='html', disable_web_page_preview=True, reply_markup=play_casino_kb.as_markup())
            return
        if int(rx) == 4:
            summ = int(summ * 0.75)
            user.edit('balance', user.balance - summ)
            return await message.reply(
                f'{rsmile} {user.link}, вы проиграли {to_str(summ)}  x0.75 {rloser}',
                parse_mode='html', disable_web_page_preview=True, reply_markup=play_casino_kb.as_markup())
        if int(rx) == 5:
            return await message.reply(
                f'♣ {user.link}, деньги остаются у вас {to_str(summ)}  x1 {rwin}',
                parse_mode='html', disable_web_page_preview=True, reply_markup=play_casino_kb.as_markup())

        if int(rx) == 6:
            summ = int(summ * 1.25)
            user.edit('balance', user.balance + summ - ssumm)
            return await message.reply(
                f'{rsmile} {user.link}, вы выиграли {to_str(summ)}  x1.25 {rwin}',
                parse_mode='html', disable_web_page_preview=True, reply_markup=play_casino_kb.as_markup())
        if int(rx) == 7:
            summ = int(summ * 1.5)
            user.edit('balance', user.balance + summ - ssumm)
            return await message.reply(
                f'{rsmile} {user.link}, вы выиграли {to_str(summ)}  x1.5 {rwin}',
                parse_mode='html', disable_web_page_preview=True, reply_markup=play_casino_kb.as_markup())
        if int(rx) == 8:
            summ = int(summ * 1.75)
            user.edit('balance', user.balance + summ - ssumm)
            return await message.reply(
                f'{rsmile} {user.link}, вы выиграли {to_str(summ)}  x1.75 {rwin}',
                parse_mode='html', disable_web_page_preview=True, reply_markup=play_casino_kb.as_markup())
        if int(rx) == 9:
            summ = int(summ * 2)
            user.edit('balance', user.balance + summ - ssumm)
            return await message.reply(
                f'{rsmile} {user.link}, вы выиграли {to_str(summ)}  x2 {rwin}',
                parse_mode='html', disable_web_page_preview=True, reply_markup=play_casino_kb.as_markup())
        if int(rx) == 10:
            summ = int(summ * 3)
            user.edit('balance', user.balance + summ - ssumm)
            return await message.reply(
                f'{rsmile} {user.link}, вы выиграли {to_str(summ)}  x3 {rwin}',
                parse_mode='html', disable_web_page_preview=True, reply_markup=play_casino_kb.as_markup())
