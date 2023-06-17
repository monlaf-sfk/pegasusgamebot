from aiogram import flags
from aiogram.types import Message

from keyboard.main import inv_kb
from utils.items.items import items, item_case, works_items
from utils.logs import writelog
from utils.main.cash import to_str
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
            text = '🎒 Ваш инвентарь:\n\n'
            user.items = list(user.items)
            count = 1
            for index, item in enumerate(user.items, start=1):
                try:
                    if item[0] > 21:
                        ind = item[1]
                        item = works_items[item[0]]
                        text += f'<code>{index}</code> • <b>{item["name"]} {item["emoji"]} (<code>x{ind}</code>)</b>\n'
                        count += 1
                    else:
                        ind = item[1]
                        item = items[item[0]]
                        text += f'<code>{index}</code> • <b>{item["name"]} {item["emoji"]} (<code>x{ind}</code>)</b>\n'
                        count += 1
                except Exception as ex:
                    print(f'{item}: {ex}')
            user.cases = list(user.cases)
            for index, item in enumerate(user.cases, start=count):
                try:
                    ind = item[1]
                    item = item_case[item[0]]
                    text += f'<code>{index}</code> • <b>{item["name"]} {item["emoji"]} (<code>x{ind}</code>)</b>\n'
                except Exception as ex:
                    print(f'{item}: {ex}')
            if text == '🎒 Ваш инвентарь:\n\n':
                return await message.reply('🎒 Ваш инвентарь пуст!')
            return await message.reply(text=text, reply_markup=inv_kb.as_markup())
        elif arg[0].lower() in ['дать', 'передать'] and len(arg) >= 3:
            if not arg[1].isdigit():
                return await message.reply('❌ Ошибка. Неверное значение номера предмета!')
            if arg[2].isdigit():
                if not message.reply_to_message and (len(arg) < 4 or not '@' in arg[3]):
                    return await message.reply(
                        '❌ Ошибка. Вы не указали кому передать или не ответили на сообщение кому '
                        'хотите передать!')
                elif not message.reply_to_message:
                    try:
                        to_user = User(username=arg[3].replace('@', ''))
                    except:
                        return await message.reply('❌ Ошибка. Неверный никнейм!')
                else:
                    to_user = User(user=message.reply_to_message.from_user)
                count = int(arg[2])
            else:
                return await message.reply('❌ Ошибка. Неверное кол-во предмета!')
            if user.id == to_user.id:
                return await message.reply('❌ Ошибка. Самому себе нельзя передать предмет!')
            user.items = list(user.items)
            if int(arg[1]) > len(user.items) or int(arg[1]) <= 0:
                return await message.reply('❌ Ошибка. Неверное значение номера предмета!')
            item = user.get_item(item_index=int(arg[1]) - 1)

            if count <= 0 or count > item[1]:
                return await message.reply('❌ Ошибка. Неверное значение кол-ва предметов!')

            if item[0] > 21:
                item_s = works_items[item[0]]
            else:
                item_s = items[item[0]]
            user.set_item(item_index=int(arg[1]) - 1, x=-count)
            to_user.items = list(to_user.items)
            to_user.set_item(item_id=item[0], x=count)
            await message.reply(f'✅ Вы успешно передали (<code>x{count}</code>) <b>{item_s["name"]}'
                                f' {item_s["emoji"]}</b> пользователю {to_user.link}', disable_web_page_preview=True)
            await writelog(message.from_user.id, f'Передача {item_s["name"]} (x{count}) юзеру {to_user.link}')
            return

        elif arg[0].lower() == 'продать' and len(arg) >= 2:
            if not arg[1].isdigit() and arg[1].lower() not in ['всё', 'все']:
                return await message.reply('❌ Ошибка. Неверное значение номера предмета!')
            count = 1
            user.items = list(user.items)

            if arg[1].lower() not in ['всё', 'все']:
                if len(arg) >= 3:
                    try:
                        if arg[2].lower() in ['всё', 'все']:
                            count = user.get_item(item_index=int(arg[1]) - 1)[1]
                        else:
                            count = int(arg[2])
                    except:
                        return await message.reply('❌ Ошибка. Неверное значение кол-ва предметов!')
                item = user.get_item(item_index=int(arg[1]) - 1)

                if count < 0 or count > item[1]:
                    return await message.reply('❌ Ошибка. Неверное значение кол-ва предметов!')
                if item[0] > 21:
                    item_s = works_items[item[0]]
                else:
                    item_s = items[item[0]]
                user.set_item(item_index=int(arg[1]) - 1, x=-count)
                user.edit('balance', user.balance + item_s["sell_price"] * count)
                await message.reply(f'✅ Вы успешно продали предмет <b>{item_s["name"]}'
                                    f' {item_s["emoji"]}</b> (<code>x{count}'
                                    f'</code>) за {to_str(item_s["sell_price"] * count)}')
                await writelog(message.from_user.id, f'Продажа {item_s["name"]} x{count}')
                return
            else:
                if len(user.items) < 1:
                    return await message.reply('🎄 Ваш инвентарь пуст! Нечего продавать!')
                inven = []
                for i in user.items:
                    if i[0] > 21:
                        try:
                            inven.append(works_items[i[0]]["sell_price"] * i[1])
                        except:
                            inven.append(1)
                    else:
                        try:
                            inven.append(items[i[0]]["sell_price"] * i[1])
                        except:
                            inven.append(1)
                price = sum(inven)
                user.editmany(balance=user.balance + price,
                              items='')
                await message.reply(f'✅ Вы успешно продали все предметы с инвентаря и получили +{to_str(price)}')
                await writelog(message.from_user.id, f'Продажа всех предметов за {to_str(price)}')
                return
        else:
            return await message.reply('❌ Ошибка. Предмет нельзя использовать с инвентаря!')
    else:
        return await message.reply(
            '❌ Ошибка. Используйте: <code>Инв (продать|мои|дать) (номер) (кол-во) (username\id)</code>')
