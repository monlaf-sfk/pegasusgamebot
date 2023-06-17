import random

from aiogram import flags
from aiogram.types import Message
from filters.users import flood_handler
from config import bot_name
from keyboard.games import open_case_kb, buy_case_kb
from keyboard.generate import show_balance_kb, show_inv_kb

from utils.items.items import item_case, items, works_items

from utils.main.cash import to_str
from utils.main.users import User


@flags.throttling_key('default')
async def cases_handler(message: Message):
    flood = await flood_handler(message)
    if flood:
        arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[
            0].lower() else message.text.split()[2:]
        if len(arg) < 1:
            return await message.reply('📦 Кейсы:\n'
                                       '🥡 1. Обычный кейс - <code>$1,000,000</code>\n'
                                       '🎁 2. Средний кейс - <code>$3,000,000</code>\n'
                                       '☄️ 3. Ультра кейс - <code>$5,000,000</code>\n\n'
                                       '📦 Используйте:\n'
                                       '<code>Кейс (открыть|купить) (номер)</code> чтобы открыть/купить кейс 👻',
                                       reply_markup=buy_case_kb.as_markup())
        elif arg[0].lower() == 'открыть' and len(arg) >= 2 and arg[1].isdigit():
            index = int(arg[1])
            if index < 1 or index > 4:
                return await message.reply('❌ Ошибка. Неверный номер кейса!')
            user = User(user=message.from_user)
            user.cases = list(user.cases)
            case = item_case[index]
            it = user.get_cases(item_id=index)
            count = 1
            if len(arg) >= 4 and arg[2].isdigit() and int(arg[2]) >= 1:
                count = int(arg[2])
            if it is None or count > it[1]:
                return await message.reply(f'❌ Ошибка. У вас нет предмета <b>{case["name"]} {case["emoji"]} (<code>x'
                                           f'{count}</code>)</b>',
                                           reply_markup=show_inv_kb.as_markup())
            elif count > 100:
                text = '⚠️ Можно открывать только до 100 кейсов за раз!\n'
                if message.chat.id != message.from_user.id:
                    text += '💡️ Лучше открывать их в личке с ботом, чтобы не флудить!'
                return await message.reply(text
                                           )
            user.set_case(item_id=index, x=-count)

            if index == 1:
                choice = random.choices([1, 5, 6, 7, 8, 9, 11, 10],
                                        k=sum(random.randint(1, 3) for _ in range(count)),
                                        weights=(0.5, 0.5, 0.5, 0.5, 0.5, 0.2, 0.2, 0.5))
            elif index == 2:
                choice = random.choices([1, 5, 6, 7, 8, 9, 11, 10, 13, 2, 26],
                                        k=sum(random.randint(1, 3) for _ in range(count)),
                                        weights=(0.5, 0.5, 0.5, 0.5, 0.5, 0.25, 0.25, 0.5, 0.25, 0.25, 0.25))
            elif index == 3:
                choice = random.choices([1, 5, 6, 7, 8, 9, 11, 10, 13, 12, 14, 3, 26, 31],
                                        k=sum(random.randint(1, 3) for _ in range(count)),
                                        weights=(0.5, 0.5, 0.5, 0.5, 0.5, 0.3, 0.3, 0.5, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3))
            else:
                choice = random.choices([1, 2],
                                        k=1,
                                        weights=(0.5, 0.3))

                text = f'🙃 С кейса {case["name"]} {case["emoji"]} (<code>x{count}</code>) вам выпалo:\n'
                if choice[0] == 1:
                    random_balance = random.randint(1000000, 10000000)
                    user.edit('balance', user.balance + random_balance)
                    text += f'💵 {to_str(random_balance)}\n'
                if choice[0] == 2:
                    random_coins = random.randint(1, 10)
                    user.edit('coins', user.coins + random_coins)
                    text += f'🪙 {to_str(random_coins)}\n'
                try:
                    return await message.reply(text)
                except Exception as e:
                    print(e)
            item_id = choice
            item_counts = []
            completed = {}
            for index, i in enumerate(item_id):
                if i in completed:
                    item_counts[completed[i]] += 1
                else:
                    completed[i] = len(item_counts)
                    item_counts.append(1)

            item_id = list(completed.keys())

            text = f'🙃 С кейса {case["name"]} {case["emoji"]} (<code>x{count}</code>) вам выпали такие предметы:\n <b>'

            for i, index in completed.items():
                x = i
                if i > 21:
                    i = works_items[i]
                else:
                    i = items[i]

                counts = item_counts[completed[x]]
                text += f'{i["name"]} {i["emoji"]} (<code>x{counts}</code>) - {to_str(i["sell_price"] * counts)}\n'

            text += '</b>'
            await message.reply(text, reply_markup=show_inv_kb.as_markup())

            user.items = list(user.items)
            user.set_item_many(item_ids=item_id, counts=item_counts)

            return

        elif arg[0].lower() == 'купить' and len(arg) >= 2 and arg[1].isdigit():
            index = int(arg[1])
            if index < 1 or index > 3:
                return await message.reply('❌ Ошибка. Неверный номер кейса!')
            user = User(user=message.from_user)
            case = item_case[index]
            count = 1
            if len(arg) >= 3 and arg[2].isdigit() and int(arg[2]) >= 1:
                count = int(arg[2])
            if user.balance < case["sell_price"] * count:
                return await message.reply(f'❌ Ошибка. Недостаточно денег на'
                                           f' руках чтобы купить кейс <b>{case["name"]} {case["emoji"]} (<code>x'
                                           f'{count}</code>)</b>',
                                           reply_markup=show_balance_kb.as_markup())
            user.cases = list(user.cases)
            user.edit('balance', user.balance - (case['sell_price'] * count))
            user.set_case(item_id=index, x=count)
            await message.reply(f'Вы успешно приобрели кейс <b>{case["name"]} {case["emoji"]} (<code>x'
                                f'{count}</code>)</b> за'
                                f' {to_str(case["sell_price"] * count)}',
                                reply_markup=open_case_kb.as_markup())

            return
        else:
            return await message.reply('📦 Используйте:\n'
                                       '<code>Кейс (открыть|купить) (номер)</code> чтобы открыть/купить кейс 👻')
