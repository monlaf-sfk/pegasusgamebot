from aiogram import Router, F, flags
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from config import owner_id
from filters.admin import IsOwner
from keyboard.main import promo_switch

from utils.main.cash import to_str, get_cash
from utils.main.db import sql
from utils.main.users import User
from utils.promo.promo import Promocode, all_promo

router = Router()


@router.message(Command("promo"), IsOwner())
@flags.rate_limit(rate=1, key='promo_handler')
async def promo_handler(message: Message):
    args = message.text.split()[1:]
    try:
        name, summ, activations = tuple(args)
        xd = 1
    except:
        name, summ, activations, xd = tuple(args)
    if name in all_promo():
        return await message.reply('🚫 Такой промокод уже существует, попробуйте другое название!')
    Promocode.create(name, int(activations), get_cash(summ), int(xd), message.from_user.id)

    return await message.reply(
        f'💫 Промокод <code>{name}</code> на сумму {to_str(int(get_cash(summ)))} и кол-во активаций'
        f' <b>{activations}</b> успешно создан')


@flags.rate_limit(rate=1, key='promo_check_handler')
async def promo_check_handler(message: Message):
    if message.from_user.id == owner_id:
        args = message.text.split()[1:]
        try:
            name = args[0].lower()
        except:
            return await message.reply('❌ Ошибка. Промокод не найден!')
        if name in all_promo():
            promo = Promocode(name)
            return await message.reply(f'🏷 Название: <code>{promo.name}</code>\n'
                                       f'🆔 Создатель: <code>{promo.owner_id}</code>\n'
                                       f'➖➖➖➖➖➖➖➖➖➖➖➖\n'
                                       f'💰 Сумма: {promo.summ}\n'
                                       f'👤 Активаций: {promo.activations - len(promo.users)}/{promo.activations}\n'
                                       f'🔱 Статус: {"✅ Активен" if promo.status else "❌ Отключен"}\n'
                                       f'➖➖➖➖➖➖➖➖➖➖➖➖\n'
                                       f'👥 Активировали: {[f"<code>{i}</code>" for i in promo.users]}\n',
                                       reply_markup=promo_switch(message.from_user.id, promo.status, name).as_markup())
    user = User(user=message.from_user)
    donate_source = user.donate_source
    try:
        donate_source = int(donate_source.split(',')[0])
    except AttributeError:
        return
    if donate_source == 2 or donate_source > 4:
        args = message.text.split()[1:]
        try:
            name = args[0].lower()
        except:
            return await message.reply('❌ Ошибка. Промокод не найден!')
        if name in all_promo():
            promo = Promocode(name)
            return await message.reply(f'🏷 Название: <code>{promo.name}</code>\n'
                                       f'🆔 Создатель: <code>{promo.owner_id}</code>\n'
                                       f'➖➖➖➖➖➖➖➖➖➖➖➖\n'
                                       f'💰 Сумма: {promo.summ}\n'
                                       f'👤 Активаций: {promo.activations - len(promo.users)}/{promo.activations}\n'
                                       f'🔱 Статус: {"✅ Активен" if promo.status else "❌ Отключен"}\n'
                                       f'➖➖➖➖➖➖➖➖➖➖➖➖\n'
                                       f'👥 Активировали: {[f"<code>{i}</code>" for i in promo.users]}\n')


@flags.rate_limit(rate=1, key='promo_switch_callback')
async def promo_switch_callback(callback_query: CallbackQuery):
    promo_d, id, name = callback_query.data.split('_')
    if int(id) != callback_query.from_user.id:
        return
    else:
        promo = Promocode(name)
        if promo.status == True:
            sql.edit_data('name', name, 'status', False, 'promocodes')
            return await callback_query.message.edit_text(f'🏷 Название: <code>{promo.name}</code>\n'
                                                          f'🆔 Создатель: <code>{promo.owner_id}</code>\n'
                                                          f'➖➖➖➖➖➖➖➖➖➖➖➖\n'
                                                          f'💰 Сумма: {promo.summ}\n'
                                                          f'👤 Активаций: {promo.activations - len(promo.users)}/{promo.activations}\n'
                                                          f'🔱 Статус: ❌ Отключен\n'
                                                          f'➖➖➖➖➖➖➖➖➖➖➖➖\n'
                                                          f'👥 Активировали: {[f"<code>{i}</code>" for i in promo.users]}\n',
                                                          reply_markup=promo_switch(callback_query.from_user.id, False,
                                                                                    name).as_markup())
        else:
            sql.edit_data('name', name, 'status', True, 'promocodes')
            return await callback_query.message.edit_text(f'🏷 Название: <code>{promo.name}</code>\n'
                                                          f'🆔 Создатель: <code>{promo.owner_id}</code>\n'
                                                          f'➖➖➖➖➖➖➖➖➖➖➖➖\n'
                                                          f'💰 Сумма: {promo.summ}\n'
                                                          f'👤 Активаций: {promo.activations - len(promo.users)}/{promo.activations}\n'
                                                          f'🔱 Статус: ✅ Активен\n'
                                                          f'➖➖➖➖➖➖➖➖➖➖➖➖\n'
                                                          f'👥 Активировали: {[f"<code>{i}</code>" for i in promo.users]}\n',
                                                          reply_markup=promo_switch(callback_query.from_user.id, True,
                                                                                    name).as_markup())
