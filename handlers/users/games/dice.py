import asyncio

from aiogram import flags
from aiogram.types import Message
from config import bot_name
from keyboard.games import play_dice_kb
from keyboard.generate import show_balance_kb

from utils.main.cash import to_str, get_cash
from utils.main.users import User

from filters.users import flood_handler2, flood_handler


@flags.throttling_key('default')
async def dice_handler(message: Message):
    flood2 = await flood_handler2(message)
    flood = await flood_handler(message)
    if flood and flood2:
        arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[
            0].lower() else message.text.split()[2:]
        user = User(user=message.from_user)
        if len(arg) < 2:
            return await message.reply(f'{user.link}, для игры в Кубик введите «Кубик [ставка] [1-6]» 👍🏼 \n'
                                       '💡 Сумму ставки можно указывать с помощью сокращений (например «1к» - ставка на 1000), либо словами «все» (ставка на весь баланс)'
                                       , disable_web_page_preview=True,
                                       reply_markup=play_dice_kb.as_markup())
        elif not arg[0].isdigit() or not arg[1].isdigit() or int(arg[0]) <= 0:
            return await message.reply(f'{user.link}, для игры в Кубик введите «Кубик [ставка] [1-6]» 👍🏼 \n'
                                       '💡 Сумму ставки можно указывать с помощью сокращений (например «1к» - ставка на 1000), либо словами «все» (ставка на весь баланс)'
                                       , disable_web_page_preview=True,
                                       reply_markup=play_dice_kb.as_markup())

        user = User(user=message.from_user)

        summ = get_cash(arg[0] if arg[0].lower() not in ['всё', 'все'] else str(user.balance))
        index = int(arg[1])

        if summ <= 0:
            return await message.reply(f'❌ {user.link}, Ставка меньше или равна нулю', disable_web_page_preview=True)

        if user.balance < summ:
            return await message.reply(f'❌ {user.link}, Недостаточно денег на руках для ставки! 💸',
                                       disable_web_page_preview=True,
                                       reply_markup=show_balance_kb.as_markup())
        elif index < 1 or index > 6:
            return await message.reply(f'❌  {user.link}, Число должно быть от 1 до 6!', disable_web_page_preview=True)

        dice = (await message.reply_dice()).dice
        if dice.value != index:
            user.edit('balance', user.balance - summ)
            await asyncio.sleep(3)
            await message.reply(f'😖 Вы не угадали число, вам выпало {dice.value} а вы загадали {index}. К сожалению '
                                f'вы '
                                f'проиграли '
                                'деньги!',
                                reply_markup=play_dice_kb.as_markup())
            # await writelog(message.from_user.id, f'Кубик и проигрыш')
            return
        x = int(summ * 2)
        user.edit('balance', user.balance + x - summ)
        await asyncio.sleep(3)
        await message.reply(f'🏅 Вы угадали число! На ваш баланс зачислено +{to_str(x)}',
                            reply_markup=play_dice_kb.as_markup())
        return
