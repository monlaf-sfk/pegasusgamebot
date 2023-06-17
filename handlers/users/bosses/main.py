import random
from contextlib import suppress
from datetime import datetime, timedelta

from aiogram import flags
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, FSInputFile, InputMediaPhoto
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import armory_img
from keyboard.main import check_ls_kb
from utils.bosses import Boss
from utils.main.cash import transform2
from utils.main.db import sql

from utils.main.users import User
from utils.weapons.swords import Armory, ArmoryInv


class BosseInfoData(CallbackData, prefix="bosses_info"):
    user_id: int
    boss_id: int


class BosseAttackData(CallbackData, prefix="bosses_attack"):
    user_id: int
    boss_id: int


@flags.throttling_key('games')
async def bosses_handler(message: Message):
    if message.chat.id != message.from_user.id:
        return await message.reply("👹 Боссы доступны только в лс !", reply_markup=check_ls_kb.as_markup())
    bosses = sql.execute("SELECT * FROM bosses", fetch=True)
    if not bosses:
        return await message.reply("👹 На данный момент нету боссов !")
    keyboard = InlineKeyboardBuilder()
    for bosse in bosses:
        boss_id, hp = bosse
        boss = Boss(id=boss_id)
        keyboard.row(InlineKeyboardButton(
            text=f"• {boss.name} •",
            callback_data=BosseInfoData(user_id=message.from_user.id, boss_id=boss.id).pack()
        ))
    await message.reply_photo(photo=armory_img['boss_hall'], caption='Вот список доступных боссов',
                              reply_markup=keyboard.as_markup())


@flags.throttling_key('games')
async def bosses_callbackinfo_handler(call: CallbackQuery, callback_data: BosseInfoData):
    if callback_data.user_id != call.from_user.id:
        return await call.answer("❌ Не трожь не твое")
    try:
        boss = Boss(id=callback_data.boss_id)
    except:
        return await call.answer('👹 Босс был убит!', show_alert=True)

    top_damage = sql.execute(
        f"SELECT user_id,damage FROM user_bosses WHERE boss_id ={callback_data.boss_id} ORDER BY damage DESC LIMIT 10;",
        fetch=True)
    text = '🏆 Лидеры по урону\n'
    index = 0
    if top_damage:

        for user_top in top_damage:
            user_id, damage = user_top
            user = User(id=user_id)
            index += 1
            text += f'{index}. {user.link} - <b>{transform2(damage)} </b>\n '

    damage_your = sql.execute(
        f"SELECT damage FROM user_bosses WHERE user_id = {callback_data.user_id} and boss_id = {callback_data.boss_id}",
        commit=False, fetchone=True)
    if not damage_your:
        damage_your = 0
    else:
        damage_your = damage_your[0]
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(
        text=f"🗡️ Нанести удар",
        callback_data=BosseAttackData(user_id=call.from_user.id, boss_id=boss.id).pack()
    ))
    with suppress(TelegramBadRequest):
        photo = InputMediaPhoto(media=boss.photo,
                                caption=f'{boss.text}{text}\nТвой урон: <b>{transform2(damage_your)}</b>')
        msg = await call.message.edit_media(media=photo, reply_markup=keyboard.as_markup())
        boss.photo = msg.photo[0].file_id


@flags.throttling_key('default')
async def bosses_callbackatttack_handler(call: CallbackQuery, callback_data: BosseAttackData):
    if callback_data.user_id != call.from_user.id:
        return await call.answer("❌ Не трожь не твое")
    try:
        boss = Boss(id=callback_data.boss_id)
    except:
        return await call.answer('Босс был убит!', show_alert=True)

    user_bosse = sql.execute(
        f"SELECT * FROM user_bosses WHERE user_id = {callback_data.user_id} AND boss_id ={callback_data.boss_id}",
        fetch=True)
    try:
        armory = Armory(armed=True, user_id=callback_data.user_id)
    except:
        armory = None
    if armory:
        if armory.durability > 0:
            weapon = armory.weapon
            armory.edit('durability', armory.durability - 1)
        else:
            weapon = None
    else:
        weapon = None
    if user_bosse and user_bosse[0][4] != None and user_bosse[0][4] - datetime.now() < timedelta(minutes=1):
        sql.execute(
            f"UPDATE user_bosses SET count_hit=0,reset_count=NULL WHERE user_id = {callback_data.user_id} and boss_id ={callback_data.boss_id}",
            commit=True)
        user_bosse = sql.execute(
            f"SELECT * FROM user_bosses WHERE user_id = {callback_data.user_id} AND boss_id ={callback_data.boss_id}",
            fetch=True)
    if user_bosse and user_bosse[0][3] >= 30:
        if user_bosse[0][4] == None:
            dt = datetime.now()
            td = timedelta(hours=12)
            my_date = dt + td
            sql.execute(
                f"UPDATE user_bosses SET reset_count='{my_date.strftime('%d-%m-%Y %H:%M')}' WHERE user_id = {callback_data.user_id} and boss_id ={callback_data.boss_id}",
                commit=True)
        return await call.answer('💤Ты устал и больше не можеше атаковать этого босса сегодня', show_alert=True)
    if boss.hp <= 0:
        return await call.answer('☠️ Босс был убит!\n'
                                 '⏰ Дождитесь следующего!', show_alert=True)
    armory_inv = ArmoryInv(callback_data.user_id)
    result = await boss.push(weapon, armory_inv.min_damage, armory_inv.max_damage)

    if user_bosse:
        sql.execute(
            f"UPDATE user_bosses SET count_hit=count_hit+1,damage=damage+{result['damage']}  WHERE user_id = {callback_data.user_id} and boss_id ={callback_data.boss_id}",
            commit=True)
    else:
        res = (callback_data.user_id, callback_data.boss_id, result['damage'], 1, None)
        sql.insert_data([res], table='user_bosses')

    top_damage = sql.execute(
        f"SELECT user_id,damage FROM user_bosses WHERE boss_id ={callback_data.boss_id} ORDER BY damage DESC LIMIT 10;",
        fetch=True)
    text = '🏆 Лидеры по урону\n'
    index = 0
    if top_damage:

        for user_top in top_damage:
            user_id, damage = user_top
            user = User(id=user_id)
            index += 1
            text += f'{index}. {user.link} - <b>{transform2(damage)} </b>\n'

    damage_your = sql.execute(
        f"SELECT damage FROM user_bosses WHERE user_id = {callback_data.user_id} and boss_id ={callback_data.boss_id}",
        commit=False, fetchone=True)
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(
        text=f"🗡️ Нанести удар",
        callback_data=BosseAttackData(user_id=call.from_user.id, boss_id=boss.id).pack()
    ))
    with suppress(TelegramBadRequest):
        if result['damage'] == 0:
            await call.answer('💨 Босс уклонился от вашей атаки!', show_alert=True)
        else:
            await call.answer(f'🗡️ Ты нанес {result["damage"]} урона', show_alert=True)

        photo = InputMediaPhoto(media=boss.photo,
                                caption=f'{boss.text}{text}\nТвой урон: <b>{transform2(damage_your[0])}</b>')
        msg = await call.message.edit_media(media=photo, reply_markup=keyboard.as_markup())
        boss.photo = msg.photo[0].file_id
