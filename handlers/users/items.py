from contextlib import suppress

from aiogram import flags, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message
from psycopg2._json import Json

from keyboard.main import inv_kb, settings_notifies_kb

from utils.main.cash import to_str
from utils.main.db import sql
from utils.main.users import User, Settings
from filters.users import flood_handler
from utils.items.work_items import works_items, fetch_all_workitems_counts, set_workitems_count, get_workitems_count


@flags.throttling_key('default')
async def item_handler(message: Message, bot: Bot):
    flood = await flood_handler(message)
    if flood:
        arg = message.text.split()[1:] if message.text.split()[0].lower() != 'продать' else message.text.split()
        if len(arg) > 0 and arg[0].lower() in ['инв', 'инвентарь']:
            arg = arg[1:]

        user = User(user=message.from_user)
        user_work_counts = fetch_all_workitems_counts(user.id)
        if len(arg) == 0 or arg[0].lower() == 'мой':
            text = f'🎒 {user.link}, Ваш инвентарь:\n\n'
            for index, item in enumerate(works_items.values(), start=1):
                count = user_work_counts.get(index, 0)
                if count > 0:
                    text += f'<code>{index}</code> • <b>{item["name"]} {item["emoji"]} (<code>x{count}</code>)</b>\n'

            if '•' not in text:
                text += "➖ Пустой"
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

            if count <= 0 or count > user_work_counts.get(int(arg[1]), 0):
                return await message.reply(f'❌ {user.link}, Неверное значение кол-ва предметов!',
                                           disable_web_page_preview=True)

            item_s = works_items[int(arg[1])]
            count_user = user_work_counts.get(int(arg[1]), 0) - count
            set_workitems_count(int(arg[1]), user.id, count_user)

            count_user2 = get_workitems_count(int(arg[1]), to_user.id)

            set_workitems_count(int(arg[1]), to_user.id, count_user2 + count if count_user2 else count)

            await message.reply(f'✅ {user.link}, Вы успешно передали (<code>x{count}</code>) <b>{item_s["name"]}'
                                f' {item_s["emoji"]}</b> пользователю {to_user.link}', disable_web_page_preview=True)
            settings = Settings(user.id)
            if settings.pay_notifies:
                with suppress(TelegramBadRequest):
                    await bot.send_message(to_user.id,
                                           f'[ПЕРЕВОД]\n❕ Вам передали (<code>x{count}</code>) <b>{item_s["name"]}'
                                           f' {item_s["emoji"]}</b> от пользователя {user.link}\n'
                                           f'🔔 Для настройки уведомлений введите «Уведомления»',
                                           disable_web_page_preview=True, reply_markup=settings_notifies_kb(user.id))
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
                            count = user_work_counts.get(int(arg[1]), 0)
                        else:
                            count = int(arg[2])
                    except:
                        return await message.reply(f'❌ {user.link}, Неверное значение кол-ва предметов!',
                                                   disable_web_page_preview=True)

                if count < 0 or count > user_work_counts.get(int(arg[1]), 0):
                    return await message.reply(f'❌ {user.link}, Неверное значение кол-ва предметов!',
                                               disable_web_page_preview=True)
                item_s = works_items[int(arg[1])]
                count_user = user_work_counts.get(int(arg[1]), 0) - count
                set_workitems_count(arg[1], user.id, count_user)

                user.edit('balance', user.balance + item_s["sell_price"] * count)
                await message.reply(f'✅ {user.link}, Вы успешно продали предмет <b>{item_s["name"]}'
                                    f' {item_s["emoji"]}</b> (<code>x{count}'
                                    f'</code>) за {to_str(item_s["sell_price"] * count)}',
                                    disable_web_page_preview=True)
                return
            else:
                inven = []
                for index, item in enumerate(works_items.values(), start=1):
                    count = user_work_counts.get(index, 0)
                    if count > 0:
                        inven.append(item["sell_price"] * count)
                price = sum(inven)
                if price == 0:
                    return await message.reply(f'🎄 {user.link}, Ваш инвентарь пуст! Нечего продавать!',
                                               disable_web_page_preview=True)

                sql.execute(f"UPDATE user_work_items SET count = 0 WHERE user_id={user.id}", commit=True)
                user.editmany(balance=user.balance + price)
                await message.reply(
                    f'✅ {user.link}, Вы успешно продали все предметы с инвентаря и получили +{to_str(price)}',
                    disable_web_page_preview=True)
                return
        else:
            return await message.reply(
                f'❌ {user.link},  Используйте: <code>Инв (продать|мои|дать) (номер) (кол-во) (username\id)</code>',
                disable_web_page_preview=True)
