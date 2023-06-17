from aiogram import flags
from aiogram.types import Message

import config
from utils.main.bitcoin import Bitcoin, bitcoins, to_usd
from keyboard.generate import buy_ferm_kb, bitcoin_kb, show_balance_kb, show_ferm_kb
from utils.main.cash import get_cash, to_str
from utils.main.db import sql
from filters.users import flood_handler
from utils.main.users import User


@flags.throttling_key('default')
async def bitcoin_handler(message: Message):
    flood = await flood_handler(message)
    if flood:
        try:
            arg = message.text.split()[1:] if not config.bot_name.lower() in message.text.split()[
                0].lower() else message.text.split()[2:]

            if message.text.split()[0].lower() == 'курс' or arg[0].lower() in ['курс', 'биткоин', 'биткоина']:
                return await message.reply('🔋 Текущий курс биткоина:\n'
                                           '➖➖➖➖➖➖➖➖➖➖➖➖\n'
                                           f'<b>1BTC</b> = {to_str(to_usd(1))}\n'
                                           f'<b>💹 Курс меняется раз в час.</b>')

            # if len(arg) == 0 or arg[0].lower() not in [ 'купить']:
            #     return await ferma_handler(message)
            user = User(id=message.from_user.id)
            if len(arg) == 0 and arg[0].lower() not in ['продать']:
                return await message.reply('❌ Используйте: <code>Биткоин купить (кол-во)</code>')
            elif arg[0].lower() in ['продать']:
                try:
                    if arg[1].isdigit():
                        summ = get_cash(arg[1])
                    else:
                        raise Exception('123')
                except:
                    summ = user.bitcoins
                if summ <= 0:
                    return await message.reply('😴 Кол-во BTC меньше или равно нулю!')
                elif summ > user.bitcoins:
                    return await message.reply('😴 Кол-во BTC больше чем баланс фермы!')

                # now = config.bitcoin_price() -  int(summ * 0.0005)
                # await config.set_bitcoin_price(now)
                user_summ = to_usd(summ)

                sql.executescript(f'UPDATE users SET bitcoins = bitcoins - {summ} WHERE id = {user.id};\n'
                                  f'UPDATE users SET bank = bank + {user_summ} WHERE id = {message.from_user.id};',
                                  True, False)

                await message.reply(f'✅ Вы успешно продали биткоины на сумму: {to_str(user_summ)} !')

                return
            else:
                try:
                    xa = sql.execute(f'SELECT balance FROM users WHERE id = {message.from_user.id}', False, True)[0][0]
                    summ = get_cash(arg[1]) if arg[1].lower() not in ['всё', 'все'] else int(xa / to_usd(1))
                    if summ <= 0:
                        raise Exception('123')
                except (ValueError, OverflowError):
                    return await message.reply('❌ Используйте: <code>Биткоин купить (кол-во)</code>')

                user_summ = to_usd(summ)

                if user_summ > xa:
                    return await message.reply(f'❌ Недостаточно денег на Балансе! Нужно: {to_str(user_summ)}')

                sql.executescript(f'UPDATE users SET bitcoins = bitcoins + {summ} WHERE id = {user.id};\n'
                                  f'UPDATE users SET balance = balance - {user_summ} WHERE id = {message.from_user.id};',
                                  True, False)

                await message.reply(f'✅ Вы успешно приобрели {summ} биткоинов за {to_str(user_summ)}',
                                    reply_markup=show_balance_kb.as_markup())

                # now = config.bitcoin_price() + int(summ * random.choice([0.01, 0.05, 0.04, 0.03, 0]))

                # await config.set_bitcoin_price(now)

                return
        except:
            return await message.reply('❌ Используйте: <code>Биткоин продать\купить (кол-во)</code>')


@flags.throttling_key('default')
async def videocards_handler(message: Message):
    flood = await flood_handler(message)
    if flood:
        arg = message.text.split()[1:] if not config.bot_name.lower() in message.text.split()[
            0].lower() else message.text.split()[2:]
        if len(arg) == 0 or arg[0].lower() not in ['купить']:
            return await message.reply('❌ Используйте: <code>Видеокарты купить (кол-во)</code>')

        try:
            bitcoin = Bitcoin(owner=message.from_user.id)
        except:
            bitcoin = None

        if bitcoin is None:
            return await message.reply('❌ У вас нет фермы!', reply_markup=buy_ferm_kb.as_markup())

        try:
            count = int(arg[1])
            if count <= 0:
                raise Exception('123')
        except ValueError:
            return await message.reply('❌ Используйте: <code>Видеокарты купить (кол-во)</code>')

        cc = bitcoin.videocards if bitcoin.videocards > 0 else 1

        summ = int((bitcoin.bitcoin.videoprice * count) * cc)

        if summ > sql.execute(f'SELECT balance FROM users WHERE id = {message.from_user.id}', False, True)[0][0]:
            return await message.reply(f'❌ Недостаточно денег на руках, нужно: {to_str(summ)}',
                                       reply_markup=show_balance_kb.as_markup())
        user = User(id=message.from_user.id)
        donate = 0
        if user.donate:
            item = config.donates[user.donate.id]
            donate = item['videocards']
        have_place = bitcoin.limit_video - bitcoin.videocards if donate == 0 else donate + bitcoin.limit_video - bitcoin.videocards
        if count + bitcoin.videocards > bitcoin.limit_video + donate:
            return await message.reply(
                f'❌ Вы превышаете лимит видеокарт, вам доступно еще:  {have_place if have_place >= 0 else 0} шт.',
                reply_markup=show_balance_kb.as_markup())
        sql.executescript(f'UPDATE bitcoin SET videocards = videocards + {count} WHERE owner = {bitcoin.owner};\n'
                          f'UPDATE users SET balance = balance - {summ} WHERE id = {message.from_user.id};',
                          True, False)

        return await message.reply(f'✅ Вы успешно приобрели {count} видеокарт(у) за {to_str(summ)}',
                                   reply_markup=show_ferm_kb.as_markup())


numbers_emoji = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']


@flags.throttling_key('default')
async def ferma_handler(message: Message):
    flood = await flood_handler(message)
    if flood:
        try:
            bitcoin = Bitcoin(owner=message.from_user.id)
        except:
            bitcoin = None

        arg = message.text.split()[1:] if not config.bot_name.lower() in message.text.split()[
            0].lower() else message.text.split()[2:]
        if (len(arg) == 0 and bitcoin is None) or (len(arg) > 0 and arg[0].lower() in ['список']):
            text = '🖥️ Список биткоин-ферм:\n'
            for index, i in bitcoins.items():
                i = i()
                emoji = ''.join(numbers_emoji[int(i)] for i in str(index))
                text += f'{emoji}. <b>{i.name}</b> \n' \
                        f'💵 Цена: {to_str(i.price)} \n' \
                        f'💱 Доход: <code>{i.doxod} BTC</code> \n' \
                        f'💲 Налог: <code>{to_str(i.nalog)}</code>\n\n'
            return await message.reply(text=text, reply_markup=buy_ferm_kb.as_markup())

        elif len(arg) > 0 and arg[0].lower() == 'купить':
            try:
                index = int(arg[1])
                if index < 1 or index > len(bitcoins):
                    raise Exception('123')
            except:
                return await message.reply('❌ Неверный номер фермы! 1-4')
            xa = sql.execute(f'SELECT balance FROM users WHERE id = {message.from_user.id}', False, True)[0][0]
            b = bitcoins[index]()
            x = b.price
            if x > xa:
                return await message.reply(f'❌ Недостаточно денег на балансе! Нужно: {to_str(x)}',
                                           reply_markup=show_balance_kb.as_markup())
            Bitcoin.create(message.from_user.id, index)
            sql.execute(f'UPDATE users SET balance = balance - {b.price} WHERE id = {message.from_user.id}',
                        True, False)
            return await message.reply(f'✅ Вы успешно приобрели ферму <b>{b.name}</b> за {to_str(x)}',
                                       reply_markup=show_ferm_kb.as_markup())

        elif bitcoin is None:
            return await message.reply('❌ У вас нет фермы!', reply_markup=buy_ferm_kb.as_markup())
        elif len(arg) == 0 and bitcoin:
            return await message.reply(text=bitcoin.text(message.from_user.id), reply_markup=bitcoin_kb.as_markup())
        elif len(arg) < 1:
            return await message.reply('❌ Используйте: <code>Ферма купить\продать\снять\налог (сумма)</code>')

        elif arg[0].lower() == 'продать':
            price = bitcoin.sell()
            if price > 0:
                sql.execute(f'UPDATE users SET balance = balance + {price} WHERE id = {message.from_user.id}',
                            True, False)
            return await message.reply(f'✅ Вы успешно продали ферму за {to_str(price)}')

        elif arg[0].lower() in ['снять', 'вывести']:
            try:
                if arg[1].isdigit():
                    summ = get_cash(arg[1])
                else:
                    raise Exception('123')
            except:
                summ = bitcoin.balance_
            if summ <= 0:
                return await message.reply('😴 Кол-во BTC меньше или равно нулю!')
            elif summ > bitcoin.balance_:
                return await message.reply('😴 Кол-во BTC больше чем баланс фермы!')

            sql.executescript(f'UPDATE bitcoin SET balance = round(balance - {summ}) WHERE owner = {bitcoin.owner};\n'
                              f'UPDATE users SET bitcoins = bitcoins + {summ} WHERE id = {message.from_user.id};',
                              True, False)

            await message.reply(f'✅ Вы успешно сняли {summ} биткоинов с биткоин фермы!')

            return

        elif arg[0].lower() in ['налог', 'налоги']:
            try:
                if arg[1].isdigit():
                    summ = get_cash(arg[1])
                else:
                    raise Exception('123')
            except:
                summ = bitcoin.nalog

            if summ <= 0:
                return await message.reply('😴 Сумма меньше или равна нулю!')
            elif summ > bitcoin.nalog:
                return await message.reply('😴 Сумма больше чем налог фермы!')
            elif sql.execute(f'SELECT bank FROM users WHERE id = {message.from_user.id}', False, True)[0][0] < summ:
                return await message.reply('❌ Недостаточно денег в банке '
                                           f'для оплаты налогов, нужно: {to_str(bitcoin.nalog)}',
                                           reply_markup=show_balance_kb.as_markup())
            sql.executescript(f'UPDATE bitcoin SET nalog = nalog - {summ} WHERE owner = {bitcoin.owner};\n'
                              f'UPDATE users SET bank = bank - {summ} WHERE id = {message.from_user.id};',
                              True, False)

            return await message.reply(f'✅ Вы успешно оплатили налог с банка!',
                                       reply_markup=show_ferm_kb.as_markup())
        else:
            return await message.reply('❌ Используйте: <code>Ферма купить\продать\снять\налог (сумма)</code>')
