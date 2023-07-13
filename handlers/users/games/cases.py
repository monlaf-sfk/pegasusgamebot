import random

from aiogram import flags
from aiogram.types import Message
from filters.users import flood_handler
from config import bot_name, donates
from keyboard.games import open_case_kb, buy_case_kb
from keyboard.generate import show_balance_kb, show_inv_kb

from utils.items.items import item_case

from utils.main.cash import to_str, to_str4
from utils.main.db import sql
from utils.main.users import User
from utils.weapons.swords import ArmoryInv


@flags.throttling_key('default')
async def cases_handler(message: Message):
    flood = await flood_handler(message)
    if flood:
        user = User(user=message.from_user)
        arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[
            0].lower() else message.text.split()[2:]
        if len(arg) < 1:
            text = '📦 Ваши кейсы:\n'
            for index, item in enumerate(user.cases, start=1):
                if user.cases[f"{index}"]["count"] > 0:
                    text += f'  🔹 №{index} » • <b>{user.cases[f"{index}"]["name"]} {user.cases[f"{index}"]["emoji"]} (<code>x{user.cases[f"{index}"]["count"]}</code>)</b>\n'

            return await message.reply('📦 Кейсы:\n'
                                       '🥡 1. Обычный кейс - <code>$10,000,000</code>\n'
                                       '🎁 2. Средний кейс - <code>$30,000,000</code>\n'
                                       '☄️ 3. Ультра кейс - <code>$50,000,000</code>\n\n'
                                       f'{text}\n'
                                       '📦 Для открытия кейсов введите «Кейс о [номер кейса] [количество: 1-5]»\n\n'
                                       '💸 Продажа кейсов: «Кейс продать [номер] [кол-во]»',
                                       reply_markup=buy_case_kb.as_markup())
        elif arg[0].lower() == 'открыть' and len(arg) >= 2 and arg[1].isdigit():
            index = int(arg[1])
            if index < 1 or index > 6:
                return await message.reply('❌ Ошибка. Неверный номер кейса!')

            case = item_case[index]
            it = user.cases[f"{index}"]
            count = 1
            if len(arg) >= 3 and arg[2].isdigit() and int(arg[2]) >= 1:
                count = int(arg[2])
            if it is None or count > it['count']:
                return await message.reply(f'❌ Ошибка. У вас нет предмета <b>{case["name"]} {case["emoji"]} (<code>x'
                                           f'{count}</code>)</b>',
                                           reply_markup=show_inv_kb.as_markup())

            if count > 1 and not user.donate:
                text = '⚠️ Можно открывать только 1 кейс за раз!\n'
                if message.chat.id != message.from_user.id:
                    text += '💡️ Лучше открывать их в личке с ботом, чтобы не флудить!\n\n'

                text += '\n<u>У 🌟 PREMIUM игроков возможно открытие до 6 кейсов за раз!</u>\n'

                return await message.reply(text)
            elif user.donate and count > donates[user.donate.id]['open_case']:
                text = f'⚠️ Можно открывать только {donates[user.donate.id]["open_case"]} кейс(a\ов) за раз!\n'
                if message.chat.id != message.from_user.id:
                    text += '💡️ Лучше открывать их в личке с ботом, чтобы не флудить!'
                return await message.reply(text)
            count_user = it['count'] - count
            sql.execute(
                "UPDATE users SET cases = jsonb_set(cases, "
                f"'{{{index}, count}}', "
                f"'{count_user}') WHERE id={user.id}", commit=True)
            if index == 1:
                choices = random.choices([1, 2, 3],
                                         k=sum(random.randint(1, 3) for _ in range(count)),
                                         weights=(0.5, 0.4, 0.3))
                range_money = 6_000_000
                range_xp = 50
                range_bitcoins = 100
            elif index == 2:
                choices = random.choices([1, 2, 3, 4],
                                         k=sum(random.randint(1, 3) for _ in range(count)),
                                         weights=(0.5, 0.4, 0.3, 0.2))
                range_money = 15_000_000
                range_xp = 150
                range_bitcoins = 300
                range_tokens = 3
            elif index == 3:
                choices = random.choices([1, 2, 3, 4],
                                         k=sum(random.randint(1, 3) for _ in range(count)),
                                         weights=(0.5, 0.4, 0.3, 0.2))
                range_money = 20_000_000
                range_xp = 300
                range_bitcoins = 800
                range_tokens = 6
            elif index == 4:
                choices = random.choices([1, 2, 3, 4],
                                         k=1,
                                         weights=(0.5, 0.4, 0.3, 0.2))

                range_money = 40_000_000
                range_xp = 600
                range_bitcoins = 1500
                range_tokens = 15
            elif index == 5:
                choices = random.choices([1, 2, 3, 4],
                                         k=1,
                                         weights=(0.5, 0.4, 0.3, 0.2))

                range_money = 30_000_000
                range_xp = 600
                range_bitcoins = 1600
                range_tokens = 30
            elif index == 6:
                choices = random.choices([1, 2, 3, 4],
                                         k=1,
                                         weights=(0.5, 0.4, 0.3, 0.2))

                range_money = 15_000_000
                range_xp = 300
                range_bitcoins = 700
                range_tokens = 10
            text = f'🙃 С кейса {case["name"]} {case["emoji"]} (<code>x{count}</code>) вам выпали такие предметы:\n '
            range_money2 = 0
            range_xp2 = 0
            range_bitcoins2 = 0
            range_tokens2 = 0
            for choice in choices:
                if choice == 1:
                    random_balance = random.randint(round(range_money / 2), range_money)
                    range_money2 += random_balance
                if choice == 2:
                    random_xp = random.randint(round(range_xp / 2), range_xp)
                    range_xp2 += random_xp
                if choice == 3:
                    random_bitcoins = random.randint(round(range_bitcoins / 2), range_bitcoins)
                    range_bitcoins2 += random_bitcoins
                if choice == 4:
                    random_tokens = random.randint(round(range_tokens / 2), range_tokens)
                    range_tokens2 += random_tokens
            if 1 in choices:
                text += f'💰 Валюта: {to_str(range_money2)}\n'
                user.edit('balance', user.balance + range_money2)
            if 2 in choices:
                text += f'💡 Опыт: {to_str4(range_xp2)}\n'
                user.edit('xp', user.xp + range_xp2)
            if 3 in choices:
                text += f'🧀 Биткоины: {to_str4(range_bitcoins2)}\n'
                user.edit('bitcoins', user.bitcoins + range_bitcoins2)
            if 4 in choices:
                text += f'💠 Токены: {to_str4(range_tokens2)}\n'
                armory_inv = ArmoryInv(user_id=user.id)
                armory_inv.edit('tokens', armory_inv.tokens + range_tokens2)
            await message.reply(text, reply_markup=show_inv_kb.as_markup())

            return
        elif arg[0].lower() == 'продать' and len(arg) >= 2 and arg[1].isdigit():
            if not arg[1].isdigit() and arg[1].lower() not in ['всё', 'все']:
                return await message.reply(f'❌ {user.link}, Неверный номер кейса!',
                                           disable_web_page_preview=True)
            count = 1
            if len(arg) >= 3:
                try:
                    if arg[2].lower() in ['всё', 'все']:
                        count = user.cases[arg[1]]['count']
                    else:
                        count = int(arg[2])
                except:
                    return await message.reply(f'❌ {user.link}, Неверное значение кол-ва кейсов!',
                                               disable_web_page_preview=True)
            if int(arg[1]) < 1 or int(arg[1]) > 3:
                return await message.reply(f'{user.link}, этот кейс нельзя продать ☹️\n'
                                           '➡️ Вы можете продавать только те кейсы, которые можно купить в магазине',
                                           disable_web_page_preview=True)
            item = user.cases[arg[1]]
            if count < 0 or count > item['count']:
                return await message.reply(f'❌ {user.link}, Неверное значение кол-ва кейсов!',
                                           disable_web_page_preview=True)
            item_s = item_case[int(arg[1])]
            sql.execute(
                "UPDATE users SET cases = jsonb_set(cases, "
                f"'{{{int(arg[1])}, count}}', "
                f"to_jsonb((cases->'{arg[1]}'->>'count')::int - {count})::text::jsonb) WHERE id={user.id}", commit=True)

            user.edit('balance', user.balance + round(item_s["price"] / 2) * count)
            await message.reply(f'✅ {user.link}, Вы успешно продали предмет <b>{item_s["name"]}'
                                f' {item_s["emoji"]}</b> (<code>x{count}'
                                f'</code>) за {to_str(round(item_s["price"] / 2) * count)}',
                                disable_web_page_preview=True)
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
            if user.balance < case["price"] * count:
                return await message.reply(f'❌ Ошибка. Недостаточно денег на'
                                           f' руках чтобы купить кейс <b>{case["name"]} {case["emoji"]} (<code>x'
                                           f'{count}</code>)</b>',
                                           reply_markup=show_balance_kb.as_markup())

            user.edit('balance', user.balance - (case['price'] * count))
            sql.execute(
                "UPDATE users SET cases = jsonb_set(cases, "
                f"'{{{int(arg[1])}, count}}', "
                f"to_jsonb((cases->'{arg[1]}'->>'count')::int + {count})::text::jsonb) WHERE id={user.id}", commit=True)
            await message.reply(f'Вы успешно приобрели кейс <b>{case["name"]} {case["emoji"]} (<code>x'
                                f'{count}</code>)</b> за'
                                f' {to_str(case["price"] * count)}',
                                reply_markup=open_case_kb.as_markup())

            return
        else:
            return await message.reply('📦 Используйте:\n'
                                       '<code>Кейс (открыть|купить) (номер)</code> чтобы открыть/купить кейс 👻')
