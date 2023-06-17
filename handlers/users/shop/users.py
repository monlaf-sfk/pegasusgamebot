import decimal

from aiogram import flags
from aiogram.types import Message
from aiogram_dialog import DialogManager

from config import bot_name
from handlers.users.shop.shop import shop_list_handler

from utils.items.items import items
from utils.main.cash import to_str
from utils.main.users import User

from filters.users import flood_handler

items_to_sell = items.copy()
del items_to_sell[-1]


@flags.throttling_key('default')
async def users_shop_handler(message: Message, dialog_manager: DialogManager):
    flood = await flood_handler(message)
    if flood:
        arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[
            0].lower() else message.text.split()[2:]
        if len(arg) > 1 and arg[0].lower() == 'купить':
            try:
                item_id = int(arg[1])
            except IndexError:
                return await message.reply('🚫 Используйте: <code>Шоп купить {номер} *{кол-во}</code>')

            try:
                item = items_to_sell[item_id]
            except KeyError:
                return await message.reply('🚫 Неверный номер предмета!')

            try:
                count = abs(int(arg[2]))
                if count == 0:
                    count = 1
            except ValueError:
                return await message.reply('🚫 Используйте: <code>Шоп купить {номер} *{кол-во}</code>')

            price = (item['sell_price'] * 2) * count
            user = User(user=message.from_user)
            if user.balance < price:
                return await message.reply(f'💲 Недостаточно средств на руках, нужно: {to_str(price)}')
            user.edit('balance', user.balance - decimal.Decimal(price))
            user.items = list(user.items)
            user.set_item(item_id=item_id, x=count)
            return await message.reply(f'💲 Вы купили {item["name"]} (x{count}) за {to_str(price)}')
        else:
            return await shop_list_handler(message, dialog_manager=dialog_manager)
