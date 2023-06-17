from aiogram import flags
from aiogram.types import Message
from filters.users import flood_handler
from config import bot_name

from utils.items.items import items
from utils.logs import writelog
from utils.main.cash import to_str, get_cash
from utils.main.users import User
from utils.promo.promo import Promocode, all_promo


@flags.throttling_key('default')
async def activatepromo_handler(message: Message):
    flood = await flood_handler(message)
    if flood:
        arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[
            0].lower() else message.text.split()[2:]
        if len(arg) == 0:
            return await message.reply('❌ Ошибка. Используйте: <code>Промо (код)</code> чтобы активировать промокод!')
        promo = arg[0].lower()
        if promo == 'создать':

            arg = arg[1:]
            if len(arg) < 3 or not arg[1] or not arg[2].isdigit():
                return await message.reply('🚫 Используйте: <code>Промо создать (название) (сумма) (активации)</code>')
            try:
                name = arg[0].lower()
                price = abs(get_cash(arg[1]))
                acts = abs(int(arg[2]))
                if price <= 1000 or acts <= 0:
                    return await message.reply(
                        '🚫 Неверное значение суммы или активаций! (мин. <code>$1,000</code> и 1 '
                        'активация)')
            except (ValueError, OverflowError):
                return await message.reply('🚫 Неверное значение суммы или активаций! (мин. <code>$1,000</code> и 1 '
                                           'активация)')
            user = User(user=message.from_user)
            if user.payban:
                return await message.reply('❌ На ваш аккаунт наложено ограничение на переводы !')
            if user.balance < price * acts:
                return await message.reply(f'🚫 Для создания такого промокода, нужно: {to_str(price * acts)}')
            elif name in all_promo():
                return await message.reply('🚫 Такой промокод уже существует, попробуйте другое название!')
            user.edit('balance', user.balance - price * acts)

            Promocode.create(name, acts, price, 1, user.id)
            await writelog(message.from_user.id, f'Создал промокод {name} на сумму {to_str(price)} и кол-во активаций '
                                                 f'{acts}')
            return await message.reply(f'🪄 Промокод <code>{name}</code> на сумму {to_str(price)} и кол-во активаций'
                                       f' <b>{acts}</b> успешно создан (-{to_str(price * acts)} с баланса)')

        if promo not in all_promo():
            return await message.reply('❌ Ошибка. Промокод не найден!')
        promo = Promocode(promo)

        if message.from_user.id in promo.users:
            return await message.reply('🙃 Вы уже активировали этот промокод!')
        elif len(promo.users) >= promo.activations:
            return await message.reply('🪄 Активации у промокода к сожалению закончились!')
        elif promo.status == False:
            return await message.reply('❌ Промокод был отключен!')

        promo.add_user(message.from_user.id)
        item = items.get(promo.summ)
        user = User(user=message.from_user)
        if item is not None:
            user.items = list(user.items)
            user.set_item(item_id=promo.summ, x=promo.xd)
            await message.reply(f'✅ Вы активировали промокод и получили:\n<b>{item["name"]} {item["emoji"]}</b> (x'
                                f'{promo.xd}) - '
                                f'{to_str(item["sell_price"])}')
            await writelog(message.from_user.id, f'Активация промокода {promo}')
            return

        user.edit('balance', user.balance + promo.summ)
        await message.reply(f'✅ Вы активировали промокод и получили +{to_str(promo.summ)}')
        await writelog(message.from_user.id, f'Активация промокода {promo}')
        return
