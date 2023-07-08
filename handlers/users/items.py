from aiogram import flags
from aiogram.types import Message
from psycopg2._json import Json

from keyboard.main import inv_kb
from utils.items.items import works_items

from utils.main.cash import to_str
from utils.main.db import sql
from utils.main.users import User
from filters.users import flood_handler


@flags.throttling_key('default')
async def item_handler(message: Message):
    flood = await flood_handler(message)
    if flood:
        arg = message.text.split()[1:] if message.text.split()[0].lower() != 'продать' else message.text.split()
        if len(arg) > 0 and arg[0].lower() in ['инв', 'инвентарь']:
            arg = arg[1:]

        user = User(user=message.from_user)
        if len(arg) == 0 or arg[0].lower() == 'мой':
            text = f'🎒 {user.link}, Ваш инвентарь:\n\n'
            for index, item in enumerate(user.items, start=1):
                text += f'<code>{index}</code> • <b>{user.items[f"{index}"]["name"]} {user.items[f"{index}"]["emoji"]} (<code>x{user.items[f"{index}"]["count"]}</code>)</b>\n'

            return await message.reply(text=text, reply_markup=inv_kb.as_markup(), disable_web_page_preview=True)
        elif arg[0].lower() in ['дать', 'передать'] and len(arg) >= 3:
            if not arg[1].isdigit():
                return await message.reply(f'❌ {user.link}, Неверное значение номера предмета!',
                                           disable_web_page_preview=True)
            if arg[2].isdigit():
                if not message.reply_to_message and (len(arg) < 4 or not '@' in arg[3]):
                    return await message.reply(
                        f'❌ {user.link}, Вы не указали кому передать или не ответили на сообщение кому '
                        'хотите передать!', disable_web_page_preview=True)
                elif not message.reply_to_message:
                    try:
                        to_user = User(username=arg[3].replace('@', ''))
                    except:
                        return await message.reply(f'❌ {user.link}, Неверный никнейм!', disable_web_page_preview=True)
                else:
                    to_user = User(user=message.reply_to_message.from_user)
                count = int(arg[2])
            else:
                return await message.reply(f'❌ {user.link}, Неверное кол-во предмета!', disable_web_page_preview=True)
            if user.id == to_user.id:
                return await message.reply(f'❌ {user.link}, Самому себе нельзя передать предмет!',
                                           disable_web_page_preview=True)

            if count <= 0 or count > user.items[arg[1]]['count']:
                return await message.reply(f'❌ {user.link}, Неверное значение кол-ва предметов!',
                                           disable_web_page_preview=True)

            item_s = works_items[int(arg[1])]

            sql.execute(
                "UPDATE users SET items = jsonb_set(items, "
                f"'{{{arg[1]}, count}}', "
                f"to_jsonb((items->'{arg[1]}'->>'count')::int + {count})::text::jsonb) WHERE id={to_user.id};"
                "UPDATE users SET items = jsonb_set(items, "
                f"'{{{arg[1]}, count}}', "
                f"to_jsonb((items->'{arg[1]}'->>'count')::int - {count})::text::jsonb) WHERE id={user.id}", commit=True)

            await message.reply(f'✅ {user.link}, Вы успешно передали (<code>x{count}</code>) <b>{item_s["name"]}'
                                f' {item_s["emoji"]}</b> пользователю {to_user.link}', disable_web_page_preview=True)
            return

        elif arg[0].lower() == 'продать' and len(arg) >= 2:
            if not arg[1].isdigit() and arg[1].lower() not in ['всё', 'все']:
                return await message.reply(f'❌ {user.link}, Неверное значение номера предмета!',
                                           disable_web_page_preview=True)
            count = 1

            if arg[1].lower() not in ['всё', 'все']:
                if len(arg) >= 3:
                    try:
                        if arg[2].lower() in ['всё', 'все']:
                            count = user.items[arg[1]]['count']
                        else:
                            count = int(arg[2])
                    except:
                        return await message.reply(f'❌ {user.link}, Неверное значение кол-ва предметов!',
                                                   disable_web_page_preview=True)
                item = user.items[arg[1]]

                if count < 0 or count > item['count']:
                    return await message.reply(f'❌ {user.link}, Неверное значение кол-ва предметов!',
                                               disable_web_page_preview=True)
                item_s = works_items[int(arg[1])]

                sql.execute(
                    "UPDATE users SET items = jsonb_set(items, "
                    f"'{{{arg[1]}, count}}', "
                    f"to_jsonb((items->'{arg[1]}'->>'count')::int - {count})::text::jsonb) WHERE id={user.id}",
                    commit=True)
                user.edit('balance', user.balance + item_s["sell_price"] * count)
                await message.reply(f'✅ {user.link}, Вы успешно продали предмет <b>{item_s["name"]}'
                                    f' {item_s["emoji"]}</b> (<code>x{count}'
                                    f'</code>) за {to_str(item_s["sell_price"] * count)}',
                                    disable_web_page_preview=True)
                return
            else:
                inven = []
                for i in user.items:
                    if user.items[i]['count'] > 0:
                        inven.append(works_items[int(i)]["sell_price"] * user.items[i]['count'])
                price = sum(inven)
                if price == 0:
                    return await message.reply(f'🎄 {user.link}, Ваш инвентарь пуст! Нечего продавать!',
                                               disable_web_page_preview=True)
                sql.execute(
                    f"UPDATE users SET items = {Json(works_items)} WHERE id={user.id}", commit=True)
                user.editmany(balance=user.balance + price)
                await message.reply(
                    f'✅ {user.link}, Вы успешно продали все предметы с инвентаря и получили +{to_str(price)}',
                    disable_web_page_preview=True)
                return
        else:
            return await message.reply(
                f'❌ {user.link},  Используйте: <code>Инв (продать|мои|дать) (номер) (кол-во) (username\id)</code>',
                disable_web_page_preview=True)
