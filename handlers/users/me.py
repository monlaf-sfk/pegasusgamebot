import re
import time
from contextlib import suppress
from datetime import timedelta, datetime

from aiogram import types, flags
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery
from typing import Union
import config
from config import bot_name
from keyboard.main import status_kb_func, status_back_kb_func, imush_back_func, imush_kb_func, settings_kb, \
    SettingsCallback, settings_action_kb, SettingsNotifiesCallback, SettingsNickCallback, settings_switch_kb, \
    settings2_switch_kb, settings3_switch_kb
from utils.city.city import City
from utils.clan.clan import Clanuser, Clan

from utils.main.airplanes import Airplane
from utils.main.bitcoin import Bitcoin
from utils.main.businesses import Business
from utils.main.cars import Car
from utils.main.cash import to_str
from utils.main.chats import Chat
from utils.main.computer import Computer
from utils.main.db import timetomin
from utils.main.houses import House
from utils.main.moto import Moto
from utils.main.users import User, Settings
from utils.main.vertoleti import Vertolet
from utils.main.yaxti import Yaxta
from utils.marries import Marry


@flags.throttling_key('default')
async def balance_handler(target: Union[types.Message, types.CallbackQuery]):
    if isinstance(target, types.CallbackQuery):
        arg = int(target.data.split('_')[2])
        if arg != target.from_user.id:
            return await target.answer(f'🤨 Убери свои шаловливые руки!')
        user = User(user=target.from_user)
        from contextlib import suppress
        with suppress(TelegramBadRequest):
            await target.message.edit_text(text=user.text, disable_web_page_preview=True,
                                           reply_markup=status_kb_func(user.id).as_markup())
        return
    arg = target.text.split()[1:] if not bot_name.lower() in target.text.split()[0].lower() else target.text.split()[2:]
    user = None
    if len(arg) > 0 and '@' in arg[0]:
        try:
            user = User(username=arg[0].replace('@', ''))
            if user.lock:
                return await target.reply('🔒 Кошелёк пользователя закрыт от других глаз!')
        except:
            user = User(user=target.from_user)
    if user is None:
        user = User(user=target.from_user)
    if len(arg) > 0 and arg[0].lower() == 'открыть':
        last = user.lock
        user.edit('lock', False)
        await target.reply(
            '🔓 Вы открыли свой кошелёк!' if last == True else '🔓 Ваш кошелёк и так был открыт!')

        return
    elif len(arg) > 0 and arg[0].lower() == 'закрыть':
        last = user.lock
        user.edit('lock', True)
        await target.reply(
            '🔒 Вы закрыли свой кошелёк!' if last == False else '🔒 Ваш кошелёк и так был закрыт!')

        return

    await target.reply(text=user.text, disable_web_page_preview=True, reply_markup=status_kb_func(user.id).as_markup())

    if target.chat.id != target.from_user.id:
        Chat(chat=target.chat)


@flags.throttling_key('default')
async def nickname_handler(message: Message):
    user = User(id=message.from_user.id)
    arg = ' '.join(message.text.split()[1:])
    args = re.sub('''[@"'%<>💎👨‍🔬🌟⚡👮‍♂👾]''', '',
                  arg.replace('[', '').replace(']', ''))
    if user.nickban:
        return await message.reply('❌ На ваш аккаунт наложено ограничение к смене ника!')
    if not args:
        return await message.reply(f'👓 Ваш никнейм: <b>{user.name if user.name else user.first_name}</b>',
                                   reply_markup=settings3_switch_kb.as_markup())
    else:
        if len(args) > 16 or len(args) < 4:
            return await message.reply('❌ Ошибка! Максимальная длина ника: 16, Минимальная: 6\n')

        user.edit('name', args)
        await message.reply(f'✅ Ваш никнейм успешно изменён на: <code>{user.link}</code>',
                            reply_markup=settings3_switch_kb.as_markup())


@flags.throttling_key('default')
async def status_handler(callbaack: CallbackQuery):
    arg = int(callbaack.data.split(':')[1])
    if arg != callbaack.from_user.id:
        return await callbaack.answer(f'🤨 Убери свои шаловливые руки!')
    user = User(id=callbaack.from_user.id)
    text = f'👤 Cтатус пользователя: {user.link}\n' \
           f'➖➖➖➖➖➖➖➖➖➖➖➖\n'
    donate = to_str(5_000_000)
    priva_name = "Игрок"
    priva_emoji = "⛹"
    description = ''
    limitvidach = 0
    if user.donate:
        item = config.donates[user.donate.id]
        donate = to_str(item['limit_dep'])
        priva_name = item['name']
        priva_emoji = item['emoji']
        description = item['description']
        if user.donate.id > 3:
            donate = '♾'
            limitvidach = item['limitvidach']
    text += f'{priva_emoji} Статус: {priva_name}\n\n' \
            f'{description}\n\n' \
            f' 💲 Возможность выдать: {to_str(user.limitvidach)}/{to_str(limitvidach)}\n' \
            f' 〽 Депозит: {to_str(user.deposit)}\{donate}\n'
    text += f'➖➖➖➖➖➖➖➖➖➖➖➖\n' \
            f'{"🚫 Ограничение на переводы" if user.payban else ""}\n' \
            f'{"🚫 Ограничение на смену ника" if user.nickban else ""}\n' \
            f'{"📛 ЧС проекта" if user.ban else ""}' \
        if user.payban or user.nickban or user.ban else ''
    with suppress(TelegramBadRequest):
        await callbaack.message.edit_text(text=text, disable_web_page_preview=True,
                                          reply_markup=status_back_kb_func(user.id).as_markup())


@flags.throttling_key('default')
async def profile_handler(target: Union[types.Message, types.CallbackQuery]):
    try:
        btc = Bitcoin(owner=target.from_user.id)
    except:
        btc = None
    user = User(id=target.from_user.id)
    donate = ""
    if user.donate:
        donate = f'┣ {user.donate.prefix} Статус: {user.donate.name}\n'
    text = f'👤 Профиль пользователя: {user.link}\n\n' \
           f'➖➖➖➖➖➖➖➖➖➖➖➖\n{donate}' \
           f'┣ 💸 Баланс: {to_str(user.balance)}\n' \
           f'┣ 🏦 В банке: {to_str(user.bank)}\n' \
           f'┣ 💳 Кредит: {to_str(user.credit)}\n' \
           f'┣ 〽️ Депозит: {to_str(user.deposit)}\n' \
           f'┞  🪙 Коины: {user.coins}\n' \
           f'┊➖➖➖➖➖➖➖➖➖➖➖\n'
    lol = datetime.now() - user.reg_date
    xd2 = f'{lol.days // 30} месяц{"ев" if lol.days // 30 > 5 else ""}' if lol.days > 30 else f'{lol.days} дней' if lol.days > 0 else f'{int(lol.total_seconds() // 3600)} часов' \
        if lol.total_seconds() > 59 else f'{int(lol.seconds)} секунд'
    xd = f' ({timetomin(int((int(user.energy_time) + 3600) - time.time()))})' if user.energy_time is not None else ''
    text += f'┟ 📅 Время в боте: {xd2}\n' \
            f'┣ 👥 Рефералы: {user.refs}\n' \
            f'┣ 🔒 Кошелёк: {"Закрыт" if user.lock else "Открыт"}\n' \
            f'┣ ⚡ Энергия: {user.energy}{xd}\n' \
            f'┣ 💡️ XP: {user.xp}\n' \
            f'┣ ⭐ BTC: <b>{btc.balance if btc else 0.0}</b>\n'
    try:
        text += f'┣ ⭐ Уровень: <b>{user.level_json.get("name")}</b>({user.level})\n'
    except:
        pass
    try:
        text += f'┗ 👻 Работа: <b>{user.job.get("name") if user.job else "Нет ❌"}</b>\n'
    except:
        pass

    text += f'➖➖➖➖➖➖➖➖➖➖➖➖\n' \
            f'{"🚫 Ограничение на переводы" if user.payban else ""}\n' \
            f'{"🚫 Ограничение на смену ника" if user.nickban else ""}\n' \
            f'{"📛 ЧС проекта" if user.ban else ""}\n' \
        if user.payban or user.nickban or user.ban else ''
    if isinstance(target, types.CallbackQuery):
        arg = int(target.data.split('_')[1])
        if arg != target.from_user.id:
            return await target.answer(f'🤨 Убери свои шаловливые руки!')
        with suppress(TelegramBadRequest):
            await target.message.edit_text(text=text, disable_web_page_preview=True,
                                           reply_markup=imush_kb_func(user.id).as_markup())
        return
    await target.reply(text=text, disable_web_page_preview=True, reply_markup=imush_kb_func(user.id).as_markup())


@flags.throttling_key('default')
async def imush_user_handler(callbaack: CallbackQuery):
    arg = int(callbaack.data.split(':')[1])
    if arg != callbaack.from_user.id:
        return await callbaack.answer(f'🤨 Убери свои шаловливые руки!')
    user = User(id=callbaack.from_user.id)
    try:
        marry = Marry(user_id=callbaack.from_user.id)
    except:
        marry = None
    try:
        business = Business(user_id=callbaack.from_user.id)
    except:
        business = None
    try:
        house = House(user_id=callbaack.from_user.id)
    except:
        house = None
    try:
        car = Car(user_id=callbaack.from_user.id)
    except:
        car = None
    try:
        yaxta = Yaxta(user_id=callbaack.from_user.id)
    except:
        yaxta = None
    try:
        vertolet = Vertolet(user_id=callbaack.from_user.id)
    except:
        vertolet = None
    try:
        airplane = Airplane(user_id=callbaack.from_user.id)
    except:
        airplane = None
    try:
        moto = Moto(user_id=callbaack.from_user.id)
    except:
        moto = None
    try:
        btc = Bitcoin(owner=callbaack.from_user.id)
    except:
        btc = None
    try:
        computer = Computer(user_id=callbaack.from_user.id)
    except:
        computer = None
    try:
        city = City(user_id=callbaack.from_user.id)
    except:
        city = None
    try:
        clanuser = Clanuser(user_id=callbaack.from_user.id)
        clan = Clan(clan_id=clanuser.clan_id)
    except:
        clanuser = None
    text = f'➖ Имущество пользователя: {user.link}\n' \
           f'┣ 🏙 Город: <b>{city.name if city else "Нет ❌"}</b>\n' \
           f'┣ ⚔ Клан: <b>{clan.name if clanuser and clan else "Нет ❌"}</b>\n' \
           f'┣ 💍 Семья: <b>{marry.name if marry and marry.name else "Есть ✅" if marry else "Нет ❌"}</b>\n' \
           f'┣ 👨‍💼 Бизнес: <b>{business.name if business else "Нет ❌"}</b>\n' \
           f'┣ 🏠 Дом: <b>{house.name if house else "Нет ❌"}</b>\n' \
           f'┣ 🏎️ Машина: <b>{car.name if car else "Нет ❌"}</b>\n' \
           f'┣ 🛳️ Яхта: <b>{yaxta.name if yaxta else "Нет ❌"}</b>\n' \
           f'┣ 🚁 Вертолёт: <b>{vertolet.name if vertolet else "Нет ❌"}</b>\n' \
           f'┣ ✈️ Самолёт: <b>{airplane.name if airplane else "Нет ❌"}</b>\n' \
           f'┣ 💻 Компьютер: <b>{computer.name if computer else "Нет ❌"}</b>\n' \
           f'┣ 🏍️ Мото: <b>{moto.name if moto else "Нет ❌"}</b>\n' \
           f'┡ 🎡 Ферма: <b>{btc.bitcoin.name if btc else "Нет ❌"}</b>\n│\n'
    xd = [business, house, car, yaxta,
          vertolet, airplane,
          moto, btc]
    nalog = sum(i.nalog for i in xd if i)

    text += f'┕💲 Налог в сумме: {to_str(nalog)}\n'
    with suppress(TelegramBadRequest):
        await callbaack.message.edit_text(text=text, disable_web_page_preview=True,
                                          reply_markup=imush_back_func(user.id).as_markup())


@flags.throttling_key('default')
async def notifies_handler(message: Message):
    user = User(user=message.from_user)
    arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[0].lower() else message.text.split()[
                                                                                                   2:]
    settings = Settings(user.id)

    if len(arg) == 0:
        text = f'🔔 Ник : {"Некликабельный ❌ " if not settings.nick_hyperlink else "Кликабельный ✅"} \n' \
               f'➡ Используйте «+Ник <code>[новый никнейм]</code>» '
        await message.reply(text=text, reply_markup=settings3_switch_kb.as_markup())
    elif arg[0].lower() == 'выкл':
        settings.edit('nick_hyperlink', False)
        text = f'🔔 Ник изменён на: Некликабельный ❌'
        await message.reply(text=text, reply_markup=settings3_switch_kb.as_markup())
    elif arg[0].lower() == 'вкл':
        settings.edit('nick_hyperlink', True)
        text = f'🔔 Ник изменён на: Кликабельный ✅'
        await message.reply(text=text, reply_markup=settings3_switch_kb.as_markup())
    else:
        text = f'🔔 Ник : {"Некликабельный ❌ " if not settings.nick_hyperlink else "Кликабельный ✅"} \n' \
               f'➡ Используйте «+Ник <code>[новый никнейм]</code>» '
        await message.reply(text=text, reply_markup=settings3_switch_kb.as_markup())


@flags.throttling_key('default')
async def settings_notifies_handler(message: Message):
    user = User(user=message.from_user)
    arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[0].lower() else message.text.split()[
                                                                                                   2:]

    settings = Settings(user.id)
    if len(arg) > 0 and arg[0].lower() == 'п':
        settings.pay_notifies = settings.edit('pay_notifies', False if settings.pay_notifies else True)
    elif len(arg) > 0 and arg[0].lower() == 'г':
        settings.city_notifies = settings.edit('city_notifies', False if settings.city_notifies else True)
    elif len(arg) > 0 and arg[0].lower() == 'б':
        settings.marry_notifies = settings.edit('marry_notifies', False if settings.marry_notifies else True)
    elif len(arg) > 0 and arg[0].lower() == 'к':
        settings.clan_notifies = settings.edit('clan_notifies', False if settings.clan_notifies else True)

    text = f"""{user.link}, настройки уведомлений:
⠀💸 [П] Переводы валюты: {'✔' if settings.pay_notifies else '❌'}️️
⠀🏙 [Г] Города: {'✔' if settings.city_notifies else '❌'}️️
⠀💞 [Б] Браки: {'✔' if settings.marry_notifies else '❌'}️️
⠀🛡 [К] Клан: {'✔' if settings.clan_notifies else '❌'}️

➡️ Для переключения введите «Увед [тип настройки (указан в скобках)]»"""
    if message.chat.type == "private":
        await message.reply(text, reply_markup=settings_action_kb(user.id, 'notifies'),
                            disable_web_page_preview=True)
    else:
        await message.reply(text, reply_markup=settings_switch_kb.as_markup(),
                            disable_web_page_preview=True)


@flags.throttling_key('default')
async def settings_handler(target: Union[types.Message, types.CallbackQuery]):
    user = User(id=target.from_user.id)
    settings = Settings(user.id)
    text = f"""
{user.link}, настройки Вашего аккаунта:
🔔 Уведомления:
  💸 Переводы валюты: {'✔' if settings.pay_notifies else '❌'}️
⠀ 🏙 Города: {'✔' if settings.city_notifies else '❌'}️️
⠀ 💞 Браки: {'✔' if settings.marry_notifies else '❌'}️️
⠀ 🛡 Клан: {'✔' if settings.city_notifies else '❌'}️️

✏️ Никнейм:
⠀ 👓 Гиперссылка: {'✔' if settings.nick_hyperlink else '❌'}️
⠀ ⚔️ Клан перед ником: {'✔' if settings.nick_clanteg else '❌'}️️
    """
    if isinstance(target, types.CallbackQuery):
        return await target.message.edit_text(text=text, reply_markup=settings_kb(user.id),
                                              disable_web_page_preview=True)
    if target.chat.type == "private":
        await target.reply(text=text, reply_markup=settings_kb(user.id), disable_web_page_preview=True)
    else:
        settings2_switch_kb.attach(settings_switch_kb)
        await target.reply(text, reply_markup=settings2_switch_kb.as_markup(),
                           disable_web_page_preview=True)


async def settings_callback(call: CallbackQuery, callback_data: SettingsCallback):
    user = User(id=call.from_user.id)
    settings = Settings(user.id)
    if callback_data.user_id != call.from_user.id:
        return await call.answer(f'🤨 Убери свои шаловливые руки!')
    if callback_data.action == 'notifies':
        text = f"""{user.link}, настройки уведомлений:
⠀💸 [П] Переводы валюты: {'✔' if settings.pay_notifies else '❌'}️️
⠀🏙 [Г] Города: {'✔' if settings.city_notifies else '❌'}️️
⠀💞 [Б] Браки: {'✔' if settings.marry_notifies else '❌'}️️
⠀🛡 [К] Клан: {'✔' if settings.clan_notifies else '❌'}️

➡️ Для переключения введите «Увед [тип настройки (указан в скобках)]»"""
    elif callback_data.action == 'nickname':
        text = f"""{user.link}, настройки для Вашего никнейма:
👓 Гиперссылка: ✔️
⚔️ Клан перед ником: ✔️

❔ Для переключения введите «Ник [вкл/выкл]», либо «Клан тег [вкл/выкл]»"""
    await call.message.edit_text(text, reply_markup=settings_action_kb(user.id, callback_data.action),
                                 disable_web_page_preview=True)


async def settings_notifies_callback(call: CallbackQuery, callback_data: SettingsNotifiesCallback):
    user = User(id=call.from_user.id)
    settings = Settings(user.id)
    if callback_data.user_id != call.from_user.id:
        return await call.answer(f'🤨 Убери свои шаловливые руки!')

    if callback_data.action == 'pay':
        settings.pay_notifies = settings.edit('pay_notifies', False if settings.pay_notifies else True)
    elif callback_data.action == 'city':
        settings.city_notifies = settings.edit('city_notifies', False if settings.city_notifies else True)
    elif callback_data.action == 'marry':
        settings.marry_notifies = settings.edit('marry_notifies', False if settings.marry_notifies else True)
    elif callback_data.action == 'clan':
        settings.clan_notifies = settings.edit('clan_notifies', False if settings.clan_notifies else True)

    text = f"""{user.link}, настройки уведомлений:
        ⠀💸 [П] Переводы валюты: {'✔' if settings.pay_notifies else '❌'}️️
        ⠀🏙 [Г] Города: {'✔' if settings.city_notifies else '❌'}️️
        ⠀💞 [Б] Браки: {'✔' if settings.marry_notifies else '❌'}️️
        ⠀🛡 [К] Клан: {'✔' if settings.clan_notifies else '❌'}️

        ➡️ Для переключения введите «Увед [тип настройки (указан в скобках)]»"""
    await call.message.edit_text(text, reply_markup=settings_action_kb(user.id, 'notifies'),
                                 disable_web_page_preview=True)


async def settings_nick_callback(call: CallbackQuery, callback_data: SettingsNickCallback):
    user = User(id=call.from_user.id)
    settings = Settings(user.id)
    if callback_data.user_id != call.from_user.id:
        return await call.answer(f'🤨 Убери свои шаловливые руки!')

    if callback_data.action == 'on_hyperlink':
        settings.edit('nick_hyperlink', True)
        text = f"{user.link}, теперь ник кликабельный 🤑"
    elif callback_data.action == 'off_hyperlink':
        settings.edit('nick_hyperlink', False)
        text = f"{user.link}, гиперссылка отключена 👍🏻"
    elif callback_data.action == 'on_clanteg':
        settings.edit('nick_clanteg', True)
        text = f"{user.link}, теперь Ваш клан отображается в нике! 👍"
    elif callback_data.action == 'off_clanteg':
        settings.edit('nick_clanteg', False)
        text = f"{user.link} отображение клана в нике отключено!"

    await call.message.edit_text(text, reply_markup=settings_action_kb(user.id, 'nick'), disable_web_page_preview=True)
