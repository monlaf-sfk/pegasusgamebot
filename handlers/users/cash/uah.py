import io

import pandas as pd
from aiogram import flags
from aiogram.types import Message, BufferedInputFile
from matplotlib import pyplot as plt

from filters.users import flood_handler
from config import bot_name
from keyboard.generate import show_balance_kb
from keyboard.cash import uah_kb, my_uah_kb
from utils.logs import writelog
from utils.main.cash import get_cash, to_str
from utils.main.db import sql
from utils.main.euro import Uah, uah_to_usd


def uah_iad():
    data = pd.read_csv('assets/uah.price', sep=' ', header=None, names=['Date', 'Time', 'Price'])

    # Преобразование столбцов в нужные форматы
    data['Date'] = pd.to_datetime(data['Date'], format='%Y-%m-%d')
    data['Time'] = pd.to_datetime(data['Time'], format='%H:%M:%S').dt.time

    # Создание столбца 'Date' для временных меток
    data['Date'] = pd.to_datetime(data['Date'].astype(str) + ' ' + data['Time'].astype(str))
    end_date = data['Date'].max()
    start_date = end_date - pd.DateOffset(days=5)
    filtered_data = data[(data['Date'] >= start_date) & (data['Date'] <= end_date)]

    # Создание графика
    dark_gray = '#333333'  # Dark gray background color
    plt.figure(figsize=(16, 11), facecolor=dark_gray, dpi=80)

    # Plot the original data as scatter points
    plt.plot(filtered_data['Date'], filtered_data['Price'], marker='o', linestyle=(0, (5, 1)), color='b',
             label='Динамика цен')

    # Smooth the curve using Exponential Moving Average (EMA)
    window_size = 5
    alpha = 2 / (window_size + 1)
    ema_smoothed = filtered_data['Price'].ewm(alpha=alpha).mean()

    # Plot the smoothed curve
    plt.plot(filtered_data['Date'], ema_smoothed, color='r', label='Сглаженная цена', linewidth=2)

    for date, price, smoothed_price in zip(filtered_data['Date'], filtered_data['Price'], ema_smoothed):
        offset_x = pd.Timedelta(minutes=30)  # Смещение по оси X
        offset_y = 5 if price > smoothed_price else -15  # Смещение по оси Y
        annotation_text = f'{price:.0f} ↑' if price > smoothed_price else f'{price:.0f} ↓'
        plt.annotate(annotation_text, (date, price), textcoords="offset points", xytext=(offset_x, offset_y),
                     ha='center', color='green')
    plt.xlabel('Дата', color='white', fontsize=25)
    plt.ylabel('Цена', color='white', fontsize=25)
    plt.title('Изменения цен на Юань', color='white', fontsize=30)
    plt.xticks(rotation=45, color='white', fontsize=12)
    plt.yticks(color='white', fontsize=12)

    # Customize legend
    plt.legend()

    # Customize grid lines
    plt.grid(True, color=dark_gray, linestyle='--', linewidth=0.5, alpha=0.7)

    # Remove spines
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)

    # Save the plot to an image buffer
    img_byte_array = io.BytesIO()
    plt.savefig(img_byte_array, format='png')
    img_byte_array.seek(0)

    # Return the image buffer
    return img_byte_array


@flags.throttling_key('default')
async def uah_handler(message: Message):
    flood = await flood_handler(message)
    if flood:
        arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[
            0].lower() else message.text.split()[2:]
        uah = Uah(owner=message.from_user.id)

        if len(arg) == 0:
            return await message.reply(uah.text, reply_markup=uah_kb.as_markup())
        elif arg[0].lower() in ['курс']:
            img = uah_iad()
            text_file = BufferedInputFile(img.getvalue(), filename="fetch.png")
            return await message.reply_photo(caption='🔋 Текущий курс Юань:\n'
                                                     '➖➖➖➖➖➖➖➖➖➖➖➖\n'
                                                     f'<b>1 💷 </b> = {to_str(uah_to_usd(1))}\n'
                                                     f'<b>💹 Курс меняется раз в час.</b>',
                                             photo=text_file)
        elif arg[0].lower() in ['купить', 'пополнить']:
            if len(arg) < 2:
                return await message.reply('❌ Используйте: <code>Юань купить (кол-во)</code>',
                                           reply_markup=my_uah_kb.as_markup())
            try:
                xa = sql.execute(f'SELECT bank FROM users WHERE id = {message.from_user.id}', False, True)[0][0]
                summ = get_cash(arg[1]) if arg[1].lower() not in ['всё', 'все'] else int(xa / uah_to_usd(1))
                if summ <= 0:
                    raise Exception('123')
            except:
                return await message.reply('🚫 Неверный ввод!')
            if (summ + uah.balance) > uah.spaciousness:
                return await message.reply('🚫 Вы превысили лимит вашей Кладовки!')
            user_summ = uah_to_usd(summ)

            if user_summ > xa:
                text = f'❌ Недостаточно денег на руках, нужно: {to_str(user_summ)}'
                if len(text) > 4095:
                    return await message.reply(f'❌ Недостаточно денег на руках\n♾ Нужно: Очень много денег!',
                                               reply_markup=show_balance_kb.as_markup())
                return await message.reply(text,
                                           reply_markup=show_balance_kb.as_markup())

            sql.executescript(f'UPDATE uah SET balance = balance + {summ} WHERE owner = {message.from_user.id};\n'
                              f'UPDATE users SET bank = bank - {user_summ} WHERE id = {message.from_user.id};',
                              True, False)

            await message.reply(f'✅ Вы успешно приобрели {summ} Юань за {to_str(user_summ)}',
                                reply_markup=my_uah_kb.as_markup())
            await writelog(message.from_user.id, f'Юань +{summ} за {to_str(user_summ)}')
            # now = uah_price() + int(summ * random.choice([0.01, 0.05, 0.04, 0.03, 0]))

            # await set_uah_price(now)

            return

        elif arg[0].lower() in ['продать', 'снять', 'обменять']:
            try:
                if arg[1].isdigit():
                    summ = get_cash(arg[1])
                else:
                    raise Exception('123')
            except:
                summ = uah.balance
            if summ <= 0:
                return await message.reply('😴 Кол-во Юань меньше или равно нулю!')
            elif summ > uah.balance:
                return await message.reply('😴 Кол-во Юань больше чем баланса Кладовки!')

            # now = uah_price() - int(summ * 0.0005)

            # await set_uah_price(now)

            user_summ = uah_to_usd(summ)

            sql.executescript(f'UPDATE uah SET balance = balance - {summ} WHERE owner = {message.from_user.id};\n'
                              f'UPDATE users SET bank = bank + {user_summ} WHERE id = {message.from_user.id};',
                              True, False)

            await message.reply(f'✅ Вы успешно сняли {to_str(user_summ)} с Кладовки!',
                                reply_markup=my_uah_kb.as_markup())
            await writelog(message.from_user.id, f'Юань -{summ} за {to_str(user_summ)}')
            return
        elif arg[0].lower() in ['улучш', 'улучшить']:
            xa = sql.execute(f'SELECT bank FROM users WHERE id = {message.from_user.id}', False, True)[0][0]
            price = 100000 * uah.level
            if xa < price:
                return await message.reply(f'🚫 Недостаточно денег в банке для улучшения, нужно: {to_str(price)}',
                                           reply_markup=my_uah_kb.as_markup())

            sql.executescript(f'UPDATE users SET bank = bank - {price} WHERE id = {message.from_user.id};\n'
                              f'UPDATE uah SET level = level + 1 WHERE owner = {message.from_user.id};')
            return await message.reply(
                f'🥫 Вы улучшили свою Кладовку Юань и теперь он вмещает: {to_str((uah.level + 1) * 1000)}',
                reply_markup=my_uah_kb.as_markup())
