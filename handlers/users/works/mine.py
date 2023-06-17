from aiogram import flags
from aiogram.types import Message
import random

from config import bot_name
from keyboard.jobs import shaxta_kb
from utils.items.items import works_items
from utils.main.cash import to_str
from utils.main.users import User
import time
from filters.users import flood_handler
from utils.weapons.swords import ArmoryInv


@flags.rate_limit(rate=1, key='mine_handler')
async def mine_handler(message: Message):
    flood = await flood_handler(message)
    if flood:
        if 'шахта' in message.text.lower():
            arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[
                0].lower() else message.text.split()[2:]
        else:
            arg = message.text.split()[1:] if bot_name.lower() in message.text.split()[
                0].lower() else message.text.split()

        user = User(user=message.from_user)

        xd = [22]
        if user.xp >= 50:
            xd.append(23)
        if user.xp >= 150:
            xd.append(24)
        if user.xp >= 500:
            xd.append(25)
        if user.xp >= 2000:
            xd.append(26)
        if user.xp >= 3000:
            xd.append(27)
        if user.xp >= 6000:
            xd.append(28)
        if len(arg) == 0:
            text = ''
            for index, i in enumerate(list(range(22, 28)), start=1):
                item = works_items[i]
                text += f'<code>{index}</code>. <b>{item["name"]} {item["emoji"]}</b> - {to_str(item["sell_price"])} (💡️ ' \
                        f'{item["xp"]})\n'
            text += f'<code>7</code>. <b>Токены 💠</b> (💡️ ' \
                    f'6000)\n'
            return await message.reply(f'⛏️ Доступные ископаемые:\n' + text + '\n\n'
                                       + f'⚡ Энергия: {user.energy}, 💡️ Опыт: {user.xp}',
                                       reply_markup=shaxta_kb.as_markup())
        elif user.energy <= 0:
            return await message.reply('⚡ У вас недостаточно энергии.')

        elif arg[0] == 'копать':
            count = 1
            if count > user.energy:
                return await message.reply('У вас нет столько энергии!')
            laste = user.energy
            user.editmany(energy=laste - count,
                          xp=user.xp + count,
                          energy_time=time.time())
            w = [8 - i for i in range(len(xd) - 1)]
            w.append(1)

            item_id = random.choices(xd, k=count, weights=w)

            if item_id[0] != 28:
                item_counts = []
                completed = {}
                for index, i in enumerate(item_id):
                    if i in completed:
                        item_counts[completed[i]] += random.randint(1, 30) if i not in [1, 5, 6, 7, 8,
                                                                                        10] else random.randint(1, 10)
                    else:
                        completed[i] = len(item_counts)
                        item_counts.append(
                            random.randint(1, 30) if i not in [1, 5, 6, 7, 8, 10] else random.randint(1, 10))

                user.items = list(user.items)
                item_id = list(completed.keys())
                user.set_item_many(item_ids=item_id, counts=item_counts)

                text = ''

                for i, index in completed.items():
                    x = i
                    i = works_items[i]
                    count = item_counts[completed[x]]
                    text += f'<code>+{count}</code> <b>{i["name"]}' \
                            f' {i["emoji"]}</b>\n'
            else:
                count = random.randint(1, 9)
                text = f'<code>+{count}</code> <b>Токены 💠</b>\n'
                armory_inv = ArmoryInv(user_id=user.id)
                armory_inv.edit('tokens', armory_inv.tokens + count)
            await message.reply(f'⛏️ Вы добыли {text}\n'
                                f'💡️ XP: <code>{user.xp}</code>\n'
                                f'⚡ Энергия: <code>{user.energy}</code>', reply_markup=shaxta_kb.as_markup())
            return
