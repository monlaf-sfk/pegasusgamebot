import decimal
import numpy as np
from aiogram import flags
from aiogram.types import Message, CallbackQuery

from config import bot_name
from filters.users import flood_handler, flood_handler2
from keyboard.games import ruletka, ruletka2
from keyboard.generate import show_balance_kb
from utils.main.cash import get_cash, to_str
from utils.main.users import User


@flags.throttling_key('games')
async def ruletka_handler_group(message: Message):
    flood2 = await flood_handler2(message)
    flood = await flood_handler(message)
    if flood and flood2:
        arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[
            0].lower() else message.text.split()[2:]
        user = User(user=message.from_user)
        if len(arg) == 0:
            return await message.reply(f'❌ {user.link}, Используйте: <code>Рулетка (<i>ставка</i>)</code>',
                                       disable_web_page_preview=True)

        try:
            summ4 = get_cash(arg[0] if arg[0].lower() not in ['всё', 'все'] else str(user.balance))
        except:
            summ4 = 0
        if user.state_ruletka is not None:
            state2 = int(user.state_ruletka.split(',')[0])
            summ2 = int(user.state_ruletka.split(',')[1])
            if state2 >= 1:
                summ = int(summ2 * 0.5 * state2 if state2 > 2 else summ2 if state2 == 1 else summ2 * 1.25)
                user.edit('balance', user.balance + decimal.Decimal(summ - summ2))
                user.edit('state_ruletka', None)
                return await message.reply(
                    f'{user.link}, Вы \n'
                    f'остановились на {state2} выстреле 🙂\n'
                    f'🔫 Осталось выстрелов: {6 - state2} [{" × " * (6 - state2)}]\n'
                    f'💸 Приз:  {to_str(summ)}\n'
                    f'💰 Баланс: {to_str(user.balance)}',

                    disable_web_page_preview=True)
            else:
                user.edit('state_ruletka', None)
                return await message.reply(f'{user.link}, Вы не сделали \n'
                                           f'ни одного выстрела 😞\n'
                                           f'🔫 Барабан: {6 - state2} [{" × " * (6 - state2)}]\n',

                                           disable_web_page_preview=True)
        if summ4 <= 0:
            return await message.reply(f'❌ {user.link}, Ставка меньше или равна нулю', disable_web_page_preview=True)

        if user.balance < summ4:
            return await message.reply(f'❌ {user.link}, Недостаточно денег на руках для ставки! 💸',
                                       disable_web_page_preview=True,
                                       reply_markup=show_balance_kb.as_markup())
        user.edit('state_ruletka', f'{0},{summ4}')
        return await message.reply(f'{user.link}, Вы начали играть в игру «Русская рулетка» \n'
                                   '🔫 Осталось выстрелов: 6 [ ×  ×  ×  ×  ×  × ]\n'
                                   '❓ Введите «Выстрел» для продолжения, либо «Ррулетка» чтобы забрать приз 👍🏼\n',
                                   disable_web_page_preview=True
                                   )


@flags.throttling_key('games')
async def rulet_push_handler_group(message: Message):
    flood2 = await flood_handler2(message)
    flood = await flood_handler(message)
    if flood and flood2:
        lot = np.random.choice([1, 2], 1, p=[0.50, 0.50])[0]
        user = User(id=message.from_user.id)
        if user.state_ruletka is None:
            return await message.reply(f"❌ {user.link}, Начни игру\n"
                                       "❓ Используйте: <code>Рулетка (<i>ставка</i>)</code>",
                                       disable_web_page_preview=True)
        state = int(user.state_ruletka.split(',')[0])
        summ = int(user.state_ruletka.split(',')[1])
        if user.balance < summ:
            return await message.reply('❌ {user.link}, Недостаточно денег на руках для ставки! 💸',
                                       disable_web_page_preview=True)
        if lot == 2:
            if state != 5:
                user.edit('state_ruletka', f'{state + 1},{summ}')
                return await message.reply(f'{user.link}, {state + 1} -й выстрел\n'
                                           f'был холостым ☺\n'
                                           f'🔫 Барабан: {6 - (state + 1)} [{" × " * (6 - (state + 1))}]\n',

                                           disable_web_page_preview=True)
            else:
                summ2 = int(summ * 0.5 * state if state > 2 else summ if state == 1 else summ * 1.25)
                user.edit('balance', user.balance + decimal.Decimal(summ2 - summ))
                user.edit('state_ruletka', None)
                return await message.reply(f'{user.link}, это был \n'
                                           f'последний выстрел,игра завершена 👍🏻 \n'
                                           f'💸 Приз:  {to_str(summ2)}\n'
                                           f'🔫 Барабан: [{" × " * (5 - state)}]',

                                           disable_web_page_preview=True)
        else:

            user.edit('balance', user.balance - summ)
            user.edit('state_ruletka', None)
            return await message.reply(f'{user.link}, произошел \n'
                                       f'выстрел️😔\n'
                                       f'❤ Потрачено на лечение: {to_str(summ)}\n'
                                       f'💰 Баланс: {to_str(user.balance)}',

                                       disable_web_page_preview=True)


@flags.throttling_key('games')
async def rulet_stop_handler_group(message: Message):
    flood2 = await flood_handler2(message)
    flood = await flood_handler(message)
    if flood and flood2:
        user = User(id=message.from_user.id)
        if user.state_ruletka is None:
            return await message.reply(f"❌ {user.link}, Начни игру\n"
                                       "❓ Используйте: <code>Рулетка (<i>ставка</i>)</code>",
                                       disable_web_page_preview=True)
        state = int(user.state_ruletka.split(',')[0])
        summ = int(user.state_ruletka.split(',')[1])
        if state >= 1:
            summ2 = int(summ * 0.5 * state if state > 2 else summ if state == 1 else summ * 1.25)
            user.edit('balance', user.balance + decimal.Decimal(summ2 - summ))
            user.edit('state_ruletka', None)
            return await message.reply(f'{user.link}, Вы \n'
                                       f'остановились на {state} выстреле 🙂\n'
                                       f'🔫 Осталось выстрелов: {6 - state} [{" × " * (6 - state)}]\n'
                                       f'💸 Приз:  {to_str(summ2)}\n'
                                       f'💰 Баланс: {to_str(user.balance)}',

                                       disable_web_page_preview=True)
        else:
            user.edit('state_ruletka', None)
            return await message.reply(f'{user.link}, Вы не сделали \n'
                                       f'ни одного выстрела 😞\n'
                                       f'🔫 Барабан: {6 - state} [{" × " * (6 - state)}]\n',

                                       disable_web_page_preview=True)
