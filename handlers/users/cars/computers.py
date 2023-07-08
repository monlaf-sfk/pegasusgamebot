import decimal
import random
import time
from contextlib import suppress
from datetime import datetime

from aiogram import flags
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery

from config import bot_name
from keyboard.generate import show_balance_kb, buy_computer_kb, show_computer_kb, show_inv_kb, \
    computer_keyboard
from utils.main.cash import to_str, get_cash
from utils.main.computer import computers, Computer
from utils.main.db import sql, timetostr
from filters.users import flood_handler
from utils.main.users import User

numbers_emoji = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']


# from aiogram_dialog.widgets.text import  Progress

class Progress():
    def __init__(
            self,
            field: str,
            width: int = 10,
            filled="🟥",
            empty="⬜",
    ):
        super().__init__()
        self.field = field
        self.width = width
        self.filled = filled
        self.empty = empty

    async def render_text(self, field) -> str:
        done = round((self.width * field) / 100)
        rest = self.width - done
        return self.filled * done + self.empty * rest + f" {field: 2.0f}%"


@flags.throttling_key('games')
async def computers_hand(call: CallbackQuery):
    user_id = int(call.data.split('_')[1])
    if user_id != call.from_user.id:
        return await call.answer(f'🤨 Убери свои шаловливые руки!')
    FIELD_PROGRESS = 1 / 10 * 100
    computer = Computer(user_id=call.from_user.id)
    user = User(id=call.from_user.id)

    if computer.last != None and (decimal.Decimal(time.time()) - computer.last) < 3600:
        times = '⌚ Вы недавно уже взламывали, нужно восстановиться!\n' \
                f'Через: {timetostr(3600 + computer.last - decimal.Decimal(time.time()))}'
        progres = await Progress(field=FIELD_PROGRESS).render_text(computer.progress)
        with suppress(TelegramBadRequest):
            await call.message.edit_text(text=computer.text.format(name=user.link, progres=progres, time=times),
                                         reply_markup=computer_keyboard(user_id), disable_web_page_preview=True)
        return
    if computer.strength <= 0:
        with suppress(TelegramBadRequest):
            await call.message.edit_text(
                text="💻 Ваш компьютер сломался для починки \nВведите команду: <code>Компьютер починить</code>",
                reply_markup=computer_keyboard(user_id), disable_web_page_preview=True)
        return
    if computer.progress >= 100:
        with suppress(TelegramBadRequest):
            computer.editmany(progress=0, cash=computer.cash + computer.computer['doxod'], last=time.time(),
                              strength=computer.strength - random.randint(1, 5))
            await call.message.edit_text(f'💻 Вы взломали и заработали {to_str(computer.computer["doxod"])}\n'
                                         f'🔋 Текущее состояние компьютера: {computer.strength}%',
                                         reply_markup=computer_keyboard(user_id))
        return
    computer.edit('progress', computer.progress + random.randint(5, 10))
    progres = await Progress(field=FIELD_PROGRESS).render_text(computer.progress)
    with suppress(TelegramBadRequest):
        await call.message.edit_text(text=computer.text.format(name=user.link, progres=progres, time=''),
                                     reply_markup=computer_keyboard(user_id), disable_web_page_preview=True)
    return


@flags.throttling_key('default')
async def computers_list_handler(message: Message):
    text = 'Список компьютеров:\n'

    for index, i in computers.items():
        emoji = ''.join(numbers_emoji[int(i)] for i in str(index))

        text += f'<code>{emoji}</code>.💻 {i["name"]} \n' \
                f'💵 Цена: {to_str(i["price"])}\n' \
                f'💱 Доход: {to_str(i["doxod"])}/час\n\n'
    return await message.reply(
        text + 'Используйте: <code>Компьютер купить</code> (номер) чтобы купить!',
        reply_markup=buy_computer_kb.as_markup())


@flags.throttling_key('default')
async def computers_handler(message: Message):
    flood = await flood_handler(message)
    if flood:
        arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[
            0].lower() else message.text.split()[2:]
        try:
            computer = Computer(user_id=message.from_user.id)

        except:
            computer = None
            if len(arg) < 1 or arg[0].lower() != 'купить':
                return await computers_list_handler(message)
            try:
                if not arg[1].isdigit():
                    return await computers_list_handler(message)
            except:
                return await computers_list_handler(message)
        if len(arg) == 0:
            user = User(id=message.from_user.id)
            FIELD_PROGRESS = 1 / 10 * 100
            progres = await Progress(field=FIELD_PROGRESS).render_text(computer.progress)
            return await message.reply(text=computer.text.format(name=user.link, progres=progres, time=''),
                                       reply_markup=computer_keyboard(user.id), disable_web_page_preview=True)
        elif arg[0].lower() in ['список', 'лист']:
            return await computers_list_handler(message)

        elif arg[0].lower() == 'продать':
            doxod = computer.sell()
            sql.execute(f'UPDATE users SET bank = bank + {doxod} WHERE id = {message.from_user.id}')
            await message.reply(f'✅ Вы продали компьютер с учётом дохода вы получили: {to_str(doxod)}',
                                reply_markup=show_balance_kb.as_markup())

            return
        elif arg[0].lower() == 'купить':
            if computer:
                return await message.reply('❗ У вас уже есть компьютер, можно иметь только 1.',
                                           reply_markup=show_computer_kb.as_markup())
            try:
                i = computers[int(arg[1])]
            except:
                return await message.reply('❌ Ошибка. Неверный номер компьютера! 1-4')
            balance = \
                sql.execute(f'SELECT balance FROM users WHERE id = {message.from_user.id}', commit=False,
                            fetchone=True)[0]
            price = i["price"]

            if balance < price:
                return await message.reply(
                    f'💲 На руках недостаточно денег для покупки, нужно: {to_str(price)}')
            Computer.create(user_id=message.from_user.id, computer_index=int(arg[1]))
            sql.execute(f'UPDATE users SET balance = balance - {price}, sell_count = 0 WHERE id ='
                        f' {message.from_user.id}', True)
            await message.reply(f'✅ Вы успешно приобрели компьютер <b>{i["name"]}</b> за'
                                f' {to_str(price)}',
                                reply_markup=show_computer_kb.as_markup())

            return
        elif arg[0].lower() in ['снять', 'доход']:
            xd = computer.cash
            if len(arg) > 1:
                try:
                    xd = get_cash(arg[1])
                except:
                    pass
            if computer.cash < xd or computer.cash < 0:
                return await message.reply('💲 Недостаточно денег на счету компьютеры!')
            elif xd <= 0:
                return await message.reply('❌ Нельзя так!')
            sql.executescript(f'''UPDATE users SET bank = bank + {xd} WHERE id = {message.from_user.id};
                                  UPDATE computers SET cash = cash - {xd} WHERE owner = {message.from_user.id};''',
                              True)

            await message.reply(f'✅ Вы успешно сняли {to_str(xd)} с прибыли компьютера!',
                                reply_markup=show_balance_kb.as_markup())

            return


        elif arg[0].lower() in ['починить', 'чинить', 'починка']:
            if computer.strength >= 100:
                return await message.reply('❌ У вас не сломан компьютер!',
                                           reply_markup=show_computer_kb.as_markup())
            items = sql.execute(f'SELECT items FROM users WHERE id = {message.from_user.id}', False, True)[0][0]

            if items['8']['count'] < 10:
                return await message.reply(
                    f"❌ Не хватает {10 - items['8']['count']} <b>Болтиков 🔩</b> для починки!'",
                    reply_markup=show_inv_kb.as_markup())

            count_items = items['8']['count'] - 10
            sql.executescript(f"UPDATE users SET items = jsonb_set(items, "
                              "'{8, count}', "
                              f"'{count_items}') WHERE id={message.from_user.id};\n"
                              f'UPDATE computers SET strength =strength+ 1 WHERE owner = {message.from_user.id};',
                              commit=True)
            await message.reply('✅ Компьютер восстановлен на +1%')

            return

        else:
            return await message.reply('❌ Ошибка. Используйте: <code>Компьютер (снять\починить) (сумма)</code>')
