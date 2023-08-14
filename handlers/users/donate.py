import random
import string

from datetime import datetime

from aiogram import flags

from aiogram.fsm.context import FSMContext

from keyboard.help import donate_help_kb, donate_back_kb
from loader import p2p, crystal, bot, crypto, payok
from states.donates import CrystalPay, CryptoBot, PayokPay

from utils.main.db import sql, write_admins_log

from aiogram.types import Message, CallbackQuery

from config import donates, crystal_in, bot_name, crypto_conf, payok_stat
from keyboard.main import donate_kb, donate_kbi, check_ls_kb, back_donate, \
    donates_kb
from keyboard.qiwi import buy_menu, buy_menu_crystal, buy_menu_crypto, buy_menu_payok
from utils.main.cash import to_str, get_cash
from utils.main.users import User


@flags.throttling_key('default')
async def donate_help_handler(message: Message):
    args = message.text.split()[1:] if not bot_name.lower() in message.text.split()[
        0].lower() else message.text.split()[
                        2:]
    if len(args) == 0:
        return await message.reply(text=actions_help['back'], reply_markup=donate_help_kb.as_markup(),
                                   disable_web_page_preview=True)
    try:
        if not args[1].lower().isdigit():
            return await message.reply('❌ Введите номер доната!')
    except IndexError:
        return await message.reply('❌ Введите номер доната!')
    arg = int(args[1].lower())
    user = User(user=message.from_user)
    if arg > 0 and arg <= 5:
        item = donates[arg]
        donate = user.donate

        if user.coins < item["price"]:
            return await message.reply(f'🪙 Недостаточно коинов, нужно: <code>{item["price"]}</code>',
                                       reply_markup=donate_kb.as_markup() if message.chat.id != message.from_user.id else donate_kbi.as_markup())
        elif donate and donate.id >= arg:
            return await message.reply('➖ У вас и так такая привилегия или выше!')
        limitvidach: int = 0
        last_vidacha = None
        if arg == 4:
            limitvidach = 10_000_000
            last_vidacha = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        if arg == 5:
            limitvidach = 30_000_000
            last_vidacha = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        user.editmany(donate_source=f'{arg},{datetime.now().strftime("%d-%m-%Y %H:%M")},True,None',
                      coins=user.coins - item['price'], limitvidach=limitvidach, last_vidacha=last_vidacha)

        return await message.reply(f'✅ Вы успешно приобрели привилегию <b>{item["name"]}</b> за {item["price"]}🪙')
    elif arg == 6:
        if user.coins < 100:
            return await message.reply(f'🪙 Недостаточно коинов, нужно: <code>100🪙</code>',
                                       reply_markup=donate_kb.as_markup() if message.chat.id != message.from_user.id else donate_kbi.as_markup())
        user.editmany(donate_videocards=user.donate_videocards + 1000, coins=user.coins - 100)
        return await message.reply(f'✅ Вы успешно приобрели <b>📼 Увеличение видеокарт x1000</b> за 100🪙')
    elif arg == 7:
        if user.coins < 150:
            return await message.reply(f'🪙 Недостаточно коинов, нужно: <code>150🪙</code>',
                                       reply_markup=donate_kb.as_markup() if message.chat.id != message.from_user.id else donate_kbi.as_markup())
        user.edit('ban_source', None)
        return await message.reply(f'✅ Вы успешно приобрели <b>👮 Разблокировку аккаунта</b> за 150🪙')
    elif arg == 8:
        if user.coins < 150:
            return await message.reply(f'🪙 Недостаточно коинов, нужно: <code>150🪙</code>',
                                       reply_markup=donate_kb.as_markup() if message.chat.id != message.from_user.id else donate_kbi.as_markup())
        user.editmany(payban=False, nickban=False)
        return await message.reply(f'✅ Вы успешно приобрели <b>⛔️ Снятие всех ограничений</b> за 150🪙')
    return await message.reply('❌ Такого доната не существует!')


actions_help = {
    'back': '''<a href="https://t.me/pegasusgame_bot">             PegasusBot🤖
    </a> 
📃 Список привилегий в боте:
➖➖➖➖➖➖➖➖➖➖➖➖
1️⃣.💎 VIP                    
2️⃣.👨‍🔬 БЕТА-ТЕСТЕР
3️⃣.🌟 PREMIUM
4️⃣.⚡ ELITE
5️⃣.👮‍♂️ ADMIN
6️⃣.🗂 Предметы
➖➖➖➖➖➖➖➖➖➖➖➖
<b>Введите:</b> <code>Задонатить</code> - чтобы задонатить

''',

    'vip': '''
📂 Название: 💎 VIP
➖➖➖➖➖➖➖➖➖➖➖➖
〽️ Увеличен процент депозита в банке до 2%
📃 Префикс в нике «💎»
💎 «VIP» отметка в профиле
🖥️ Увеличен лимит видюх до 1.100 шт.
🎁 Ежедневный бонус Увеличен на 50.000💸
💳 Максимальная сумма вклада депозита до 10.000.000$
📦 Открытие 4-х кейсов за раз
🛡 Защита от ограбления
➖➖➖➖➖➖➖➖➖➖➖➖
🔖 Цена: 200 🪙
<b>Введите:</b> <code>Донат купить 1</code> - чтобы купить привилегию
''',

    'premium': '''
📂 Привилегия: 🌟 PREMIUM
➖➖➖➖➖➖➖➖➖➖➖➖
[💎️] Все привилегии VIP
〽️ Увеличен процент депозита в банке до 3%
📃 Префикс в нике «🌟»
🌟 «PREMIUM» отметка в профиле
🖥️ Увеличен лимит видюх до 1.300 шт.
🎁 Ежедневный бонус Увеличен на 100.000💸
💳 Максимальная сумма вклада депозита до 30.000.000$
📦 Открытие 6-х кейсов за раз
➖➖➖➖➖➖➖➖➖➖➖➖
1️⃣ Инфо (id/username):
➖ Выводить информацию о игроках в боте!
➖➖➖➖➖➖➖➖➖➖➖➖
🔖 Цена: 300 🪙
<b>Введите:</b> <code>Донат купить 3</code> - чтобы купить привилегию
''',
    'beta': '''
📂 Привилегия: 👨‍🔬 БЕТА-ТЕСТЕР
➖➖➖➖➖➖➖➖➖➖➖➖
〽️ Увеличен процент депозита в банке до 2%
📃 Префикс в нике «👨‍🔬»
👨‍🔬 «БЕТА-ТЕСТЕР» отметка в профиле
🖥️ Увеличен лимит видюх до 1.200 шт.
🎁 Ежедневный бонус Увеличен на 100.000💸
💳 Максимальная сумма вклада депозита до 15.000.000$
📦 Открытие 6-х кейсов за раз
➖➖➖➖➖➖➖➖➖➖➖➖
1️⃣ /promo_check (название):
➖ Смотреть кто создал и активировал.
➖➖➖➖➖➖➖➖➖➖➖➖
🔖 Цена: 50000000 
<b>Введите:</b> <code>Донат купить 2</code> - чтобы купить привилегию🪙
''',
    'elite': '''
📂 Привилегия: ⚡ ELITE
➖➖➖➖➖➖➖➖➖➖➖➖
[💎️] Все привилегии VIP
[🌟] Все привилегии PREMIUM
〽️ Увеличен процент депозита в банке до 4%
📃 Префикс в нике «⚡»
⚡ «ELITE» отметка в профиле
🖥️ Увеличен лимит видюх до 1.500 шт.
🎁 Ежедневный бонус Увеличен на 200.000💸
💳 Максимальная сумма депозита неограничена
📦 Открытие 10-х кейсов за раз
➖➖➖➖➖➖➖➖➖➖➖➖
1️⃣ Инфо (id/username):
➖ Выводить информацию о игроках в боте!
2️⃣ Автоналоги (вкл\выкл):
➖ Автоматическая оплата налогов
3️⃣ Выдача (кол-во) (id/username):
➖ Максимум можете выдавать <code>$10,000,000</code>!
➖➖➖➖➖➖➖➖➖➖➖➖
🔖 Цена: 500 🪙
<b>Введите:</b> <code>Донат купить 4</code> - чтобы купить привилегию'''
    ,
    'admin': '''
📂 Привилегия: 👮‍♂️ ADMIN
➖➖➖➖➖➖➖➖➖➖➖➖
[💎️] Все привилегии VIP
[🌟] Все привилегии PREMIUM
[⚡] Все привилегии ELITE
📃 Префикс в нике «👮‍♂»
👮‍♂ «ADMIN» отметка в профиле
🖥️ Увеличен лимит видюх до 2.000 шт. 
🎁 Ежедневный бонус Увеличен на 400.000💸
📦 Открытие 20-х кейсов за раз
➖➖➖➖➖➖➖➖➖➖➖➖
1️⃣ Инфо (id/username):
➖ Выводить информацию о игроках в боте!
2️⃣ Автоналоги (вкл\выкл):
➖ Автоматическая оплата налогов
3️⃣ Выдача (кол-во) (id/username):
➖ Максимум можете выдавать <code>$30,000,000</code>!
4️⃣ /promo_check (название):
➖ Смотреть кто создал и активировал.
➖➖➖➖➖➖➖➖➖➖➖➖
🔖 Цена: 700 🪙
<b>Введите:</b> <code>Донат купить 5</code> - чтобы купить привилегию'''
    ,
    'subject': '''
📂 Раздел: 🗂 Предметы
➖➖➖➖➖➖➖➖➖➖➖➖
💰 <i>Курс обмена коины на доллары</i>
💵 1🪙 = {}
<b>Введите:</b> <code>Кобмен (кол-во коинов)</code> - чтобы обменять коины на деньги
➖➖➖➖➖➖➖➖➖➖➖➖

📼 Увеличение видеокарт x1000 
🔖 Цена: 100 🪙
<b>Введите:</b> <code>Донат купить 6</code>

➖➖➖➖➖➖➖➖➖➖➖➖
👮 Разблокировка аккаунта
🔖 Цена: 150 🪙
<b>Введите:</b> <code>Донат купить 7</code>

➖➖➖➖➖➖➖➖➖➖➖➖
⛔️ Снятие всех ограничений
🔖 Цена: 150 🪙
<b>Введите:</b> <code>Донат купить 8</code>
'''
}


@flags.throttling_key('default')
async def donate_help_call_handler(call: CallbackQuery):
    action = call.data.split('_')[1]
    summ = sql.execute("SELECT coin_kurs FROM other", commit=False, fetch=True)[0][0]
    text = actions_help[action]
    text = text.format(to_str(summ)) if action == 'subject' else text
    try:

        return await call.message.edit_text(text=text,
                                            reply_markup=donate_back_kb.as_markup() if action != 'back' else donate_help_kb.as_markup(),
                                            disable_web_page_preview=True)
    except:
        return await call.answer('😎')


@flags.throttling_key('default')
async def zadonatit_handler(message: Message):
    try:
        if isinstance(message, Message):
            message = message
            call = None
        else:
            call = message

        if call:
            return await call.message.edit_text(text='💳 Методы оплаты:\n'
                                                     '1. 👛 CryptoBot\n'
                                                     '2. 🥝 QIWI\n'
                                                     '3. 💎 CrystalPay\n'
                                                     '4. 🆗 Payok\n'
                                                     f'➖➖➖➖➖➖➖➖➖➖➖➖\n'
                                                     '<i> Мы рекомендуем ознакомиться с <a href="https://teletype.in/@corching/Termsofuse">пользовательским соглашением</a>, прежде чем продолжить использование данного бота.</i> \n' \
                                                     f'➖➖➖➖➖➖➖➖➖➖➖➖\n'
                                                     f'⛔ Возникли проблемы? Пишите @corching\n\n'
                                                     '💎 Выберите метод оплаты:', reply_markup=donates_kb.as_markup(),
                                                disable_web_page_preview=True)
        else:
            await bot.send_message(
                chat_id=message.from_user.id,
                text='💳 Методы оплаты:\n'
                     '1. 👛 CryptoBot\n'
                     '2. 🥝 QIWI\n'
                     '3. 💎 CrystalPay\n'
                     '4. 🆗 Payok\n'
                     f'➖➖➖➖➖➖➖➖➖➖➖➖\n'
                     '<i> Мы рекомендуем ознакомиться с <a href="https://teletype.in/@corching/Termsofuse">пользовательским соглашением</a>, прежде чем продолжить использование данного бота.</i> \n' \
                     f'➖➖➖➖➖➖➖➖➖➖➖➖\n'
                     f'⛔ Возникли проблемы? Пишите @corching\n\n'
                     '💎 Выберите метод оплаты:', reply_markup=donates_kb.as_markup(),
                disable_web_page_preview=True)
            if message.chat.id != message.from_user.id:
                return await message.reply('✈️ Я отправил вам в лс клавиатуру для доната!',
                                           reply_markup=check_ls_kb.as_markup())
    except:
        return await message.reply('🍁 Не могу отправить тебе в лс ничего, напиши мне что-то в лс ',
                                   reply_markup=check_ls_kb.as_markup())


async def other_method_handler(call: CallbackQuery):
    text = '🪙 Чтобы получить коины :\n\n' \
           '• Писать @corching \n' \
           '💰 После перевода, пишите в лс  с чеком!\n'
    return await call.message.edit_text(text=text,
                                        reply_markup=back_donate.as_markup())


async def cobmen_handler(message: Message):
    arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[0].lower() else message.text.split()[
                                                                                                   2:]
    if len(arg) == 0:
        return await message.reply('❌ Введите: <code>Кобмен {кол-во коинов}</code>')
    try:
        summ = abs(get_cash(arg[0]))
        if summ == 0:
            raise Exception('123')
    except:
        return await message.reply('❌ Введите: <code>Кобмен {кол-во коинов}</code>')

    user = User(user=message.from_user)
    if user.coins < summ:
        return await message.reply(f'🪙 Недостаточно коинов на балансе, нужно <code>{summ}</code> а у вас '
                                   f'<code>{user.coins}</code>',
                                   reply_markup=donate_kb.as_markup() if message.chat.id != message.from_user.id else donate_kbi.as_markup())
    price = sql.execute("SELECT coin_kurs FROM other", commit=False, fetch=True)[0][0]
    user.editmany(coins=user.coins - summ,
                  balance=user.balance + summ * price)

    return await message.reply(f'✅ Вы успешно обменяли {summ} коинов на {to_str(summ * price)}')


async def percent_buy_handler(message: Message):
    arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[0].lower() else message.text.split()[
                                                                                                   2:]
    user = User(user=message.from_user)

    if len(arg) == 0:
        x = f'{user.donate.percent}' if user.donate else "1"
        return await message.reply(f'😐 Ваш процент: {x}%\n')


############################################################################################
async def qiwi_info_handler(call: CallbackQuery):
    text = f'🪙 <b>Введите:</b> <code>Пополнить (<i>сумма</i>)</code>\n' \
           f'💎 Напишите сумму в <b>Рублях</b>\n' \
           f'➖➖➖➖➖➖➖➖➖➖➖➖\n' \
           f'⛔ Возникли проблемы? Пишите @corching'
    return await call.message.reply(text=text, reply_markup=back_donate.as_markup())


async def qiwi_buy_handler(message: Message):
    if message.chat.type != 'private':
        return await message.reply("❌ Пополнить можно только в личные сообщения", reply_markup=check_ls_kb.as_markup())
    arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[0].lower() else message.text.split()[
                                                                                                   2:]
    try:
        if int(arg[0]) >= 1:
            xdonate = int(sql.execute("SELECT donatex2 FROM other", commit=False, fetch=True)[0][0])
            comment = str(message.from_user.id) + \
                      "_" + str(random.randint(1000, 9999))
            bill = p2p.bill(amount=int(arg[0]),
                            lifetime=15, comment=comment)
            await message.reply(f"💸 Cумма оплаты: {arg[0]} Рублей \n"
                                f"💎 Зачисление: {f'<s>{arg[0]}</s> {int(arg[0]) * xdonate}' if xdonate > 1 else arg[0]} Коинов\n"
                                f"🛒 Нажмите по кнопки ниже для оплаты счёта\n"
                                f"⏳ Срок ссылки 15 минут !",
                                reply_markup=buy_menu(url=bill.pay_url, bill=bill.bill_id).as_markup())
        else:
            await message.reply(f'‼️Минимальная сумма 1 руб',
                                parse_mode='html')
    except:
        return await message.reply(f'❌ Ошибка. Используйте: <code>Пополнить (<i>сумма</i>)</code>',
                                   parse_mode='html')


@flags.throttling_key('default')
async def check_handler_qiwi(callback: CallbackQuery):
    bill = callback.data.split('_')[1]
    payment = p2p.check(bill_id=bill)
    if payment.status == "PAID":
        user = User(user=callback.from_user)
        xdonate = int(sql.execute("SELECT donatex2 FROM other", commit=False, fetch=True)[0][0])
        await callback.message.edit_text(
            f"🥳 Вы успешно оплатили счет на ваш баланс зачислено {int(float(payment.amount)) * xdonate} коинов")
        user.edit('coins', user.coins + (int(float(payment.amount)) * xdonate))
    else:
        await callback.answer("🚫 Вы не оплатили счет!", show_alert=True)


#########################################################################
async def crystal_info_handler(call: CallbackQuery, state: FSMContext):
    if not crystal_in:
        return await call.answer('⛔ Этот метод оплаты отключён!')
    await state.set_state(CrystalPay.start)
    text = f'🪙 Напишите сумму в <b>Рублях</b> которые вы хотите задонатить\n' \
           f'➖➖➖➖➖➖➖➖➖➖➖➖\n' \
           f'⛔ Возникли проблемы? Пишите @corching'
    return await call.message.reply(text=text)


async def crystal_buy_handler(message: Message, state: FSMContext):
    if message.chat.type != 'private':
        return await state.clear()
    await state.clear()
    if not message.text.isdigit() or int(message.text) <= 0:
        return await message.reply('❌ Неверная сумма!')
    summ = int(message.text.split()[0])
    try:
        if summ >= 2:
            xdonate = int(sql.execute("SELECT donatex2 FROM other", commit=False, fetch=True)[0][0])
            payment = await crystal.create_invoice(amount=summ, lifetime=15,
                                                   redirect_url='https://t.me/pegasusgame_bot'
                                                   )
            await message.reply(f"💸 Cумма оплаты: {payment['amount']} Рублей \n"
                                f"💎 Зачисление: {f'<s>{summ}</s> {summ * xdonate}' if xdonate > 1 else summ} Коинов\n"
                                f"🛒 Нажмите по кнопки ниже для оплаты счёта\n"
                                f"⏳ Срок ссылки 15 минут !",
                                reply_markup=buy_menu_crystal(url=payment['url'], payment_id=payment['id'],
                                                              amount=payment['amount']).as_markup())
        else:
            await message.reply(f'‼️Минимальная сумма 2 руб',
                                parse_mode='html')
    except Exception as e:
        write_admins_log(f'crystal_buy_handler:', f'{e}')
        return await message.reply(f'❌ Ошибка. Попробуйте заново!',
                                   parse_mode='html')


@flags.throttling_key('default')
async def check_handler_crystal(callback: CallbackQuery):
    action, payment_id, amount = callback.data.split(':')
    payment = await crystal.get_invoice(payment_id)
    if payment['state'] == 'payed':
        user = User(user=callback.from_user)
        xdonate = int(sql.execute("SELECT donatex2 FROM other", commit=False, fetch=True)[0][0])
        await callback.message.edit_text(
            f"🥳 Вы успешно оплатили счет на ваш баланс зачислено {payment['amount'] * xdonate} коинов!")
        user.edit('coins', user.coins + (int(payment['amount']) * xdonate))
    else:
        await callback.answer("🚫 Вы не оплатили счет!", show_alert=True)


###################################################

async def crypto_info_handler(call: CallbackQuery, state: FSMContext):
    if not crypto_conf:
        return await call.answer('⛔ Этот метод оплаты отключён!')
    await state.set_state(CryptoBot.start)
    text = f'🪙 Напишите кол-во <b>Коинов</b> которые вы хотите задонатить\n' \
           f'➖➖➖➖➖➖➖➖➖➖➖➖\n' \
           f'⛔ Возникли проблемы? Пишите @corching'
    return await call.message.reply(text=text)


async def crypto_buy_handler(message: Message, state):
    if message.chat.type != 'private':
        return await state.clear()
    await state.clear()
    if not message.text.isdigit() or int(message.text) < 10 or int(message.text) > 1000:
        return await message.reply('❌ Минимум 10 коинов = 0.1 TON , Макс. 1000 коинов')
    summ = int(message.text)
    try:
        if summ >= 10:
            summ2 = float(summ / 100)
            xdonate = int(sql.execute("SELECT donatex2 FROM other", commit=False, fetch=True)[0][0])
            invoice = await crypto.create_invoice(asset='TON', amount=summ2, expires_in=900,
                                                  description=f'Оплата {summ * xdonate} коинов')
            await message.reply(f"💸 Cумма оплаты: {summ2} TON \n"
                                f"💎 Зачисление: {f'<s>{summ}</s> {summ * xdonate}' if xdonate > 1 else summ} Коинов\n"
                                f"🛒 Нажмите по кнопки ниже для оплаты счёта\n"
                                f"⏳ Срок ссылки 15 минут !",
                                reply_markup=buy_menu_crypto(url=invoice.pay_url, invoice_id=invoice.invoice_id,
                                                             amount=summ).as_markup())

        else:
            await message.reply(f'❌️Минимум 10 коинов = 0.1 TON , Макс. 1000 коинов',
                                parse_mode='html')
    except Exception as e:
        write_admins_log(f'crypto_buy_handler:', f'{e}')
        return await message.reply(f'❌ Ошибка. Попробуйте заново!',
                                   parse_mode='html')


@flags.throttling_key('default')
async def check_handler_crypto(callback: CallbackQuery):
    action, payment_id, amount = callback.data.split(':')
    invoices = await crypto.get_invoices(invoice_ids=payment_id)
    invoices = invoices[0]
    if invoices.status == 'paid':
        user = User(user=callback.from_user)
        xdonate = int(sql.execute("SELECT donatex2 FROM other", commit=False, fetch=True)[0][0])
        await callback.message.edit_text(
            f"🥳 Вы успешно оплатили счет на ваш баланс зачислено {int(amount) * xdonate} коинов!")
        user.edit('coins', user.coins + (int(amount) * xdonate))
    elif invoices.status == 'expired':
        await callback.answer("🚫 Срок счета истек!", show_alert=True)
    else:
        await callback.answer("🚫 Вы не оплатили счет!", show_alert=True)


###################################################

async def payok_info_handler(call: CallbackQuery, state: FSMContext):
    if not payok_stat:
        return await call.answer('⛔ Этот метод оплаты отключён!')
    await state.set_state(PayokPay.start)
    text = f'🪙 Напишите кол-во в <b>Рублях</b> которые вы хотите задонатить\n' \
           f'➖➖➖➖➖➖➖➖➖➖➖➖\n' \
           f'⛔ Возникли проблемы? Пишите @corching'
    return await call.message.reply(text=text)


async def payok_buy_handler(message: Message, state):
    if message.chat.type != 'private':
        return await state.clear()
    await state.clear()
    if not message.text.isdigit() or int(message.text) < 1:
        return await message.reply('❌ Минимальная сумма оплаты = 1 рубль.')
    summ = int(message.text)
    try:
        if summ >= 1:
            xdonate = int(sql.execute("SELECT donatex2 FROM other", commit=False, fetch=True)[0][0])

            # add_check_crystal(user.id,
            #           int(arg[0]), payment.id,crystal_time=time.time())
            payment = "".join(random.choice(string.ascii_letters + '0123456789') for _ in range(random.randint(16, 30)))

            invoice = await payok.create_pay(amount=summ,
                                             payment=payment,
                                             desc=f'Оплата {summ * xdonate} коинов',
                                             currency='RUB')
            await message.reply(f"💸 Cумма оплаты: {summ} RUB \n"

                                f"💎 Зачисление: {f'<s>{summ}</s> {summ * xdonate}' if xdonate > 1 else summ} Коинов\n"
                                f"🛒 Нажмите по кнопки ниже для оплаты счёта\n"
                                f"⏳ Срок ссылки 15 минут !",
                                reply_markup=buy_menu_payok(url=invoice, invoice_id=payment).as_markup())
        else:
            await message.reply(f'❌ Минимальная сумма оплаты = 1 рубль.',
                                parse_mode='html')
    except Exception as e:
        write_admins_log(f'payok_buy_handler:', f'{e}')
        return await message.reply(f'❌ Ошибка. Попробуйте заново!',
                                   parse_mode='html')


@flags.throttling_key('default')
async def check_handler_payok(callback: CallbackQuery):
    payment = callback.data.split(':')[1]
    try:
        invoices = await payok.get_transactions(payment=payment)
    except Exception as e:
        write_admins_log(f'check_handler_payok:', f'{e}')
        return

    if invoices.transaction_status == 1:
        write_admins_log(f'PAYOK:', f'{invoices}')
        user = User(user=callback.from_user)
        xdonate = int(sql.execute("SELECT donatex2 FROM other", commit=False, fetch=True)[0][0])
        await callback.message.edit_text(
            f"🥳 Вы успешно оплатили счет на ваш баланс зачислено {int(invoices.currency_amount) * xdonate} коинов!")
        user.edit('coins', user.coins + (int(invoices.currency_amount) * xdonate))
    else:
        await callback.answer("🚫 Вы не оплатили счет!", show_alert=True)
