import asyncio
import random
from contextlib import suppress
from datetime import datetime, timedelta
import decimal
import time

import numpy as np
from aiogram import flags, Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery

from config import bot_name
from filters.triggers import Trigger
from keyboard.clans import war_clan, war_clan_info, war_clan_member
from utils.clan.clan import Clanuser, Clan
from utils.clan.clanwar import ClanWar, ClanWarFind, ClanWarMember
from utils.main.donates import to_str as unix_date
from utils.main.db import sql, timetostr
from utils.main.users import User, Settings
from utils.quests.main import QuestUser
from utils.weapons.swords import Armory, ArmoryInv

router = Router()
router.message.filter(F.chat.type.in_({"private"}))


async def attack_clan(weapon: dict = None, min_damage: int = 1, max_damage: int = 1):
    x = random.randint(min_damage, max_damage)
    if weapon:
        x += random.randint(weapon["min_attack"], weapon["max_attack"])
        crit_chance = np.random.choice([1, 2], 1,
                                       p=[1 - weapon["crit_chance"] * 0.01, weapon["crit_chance"] * 0.01])[0]

        if crit_chance == 2:
            x += x * weapon["crit_multi"] * 0.01

    return x


@router.message(Trigger(["кв"]))
@flags.throttling_key('default')
async def clan_handler(message: Message, bot: Bot):
    arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[
        0].lower() else message.text.split()[2:]

    user = User(id=message.from_user.id)
    try:
        clanuser = Clanuser(user_id=message.from_user.id)
    except:
        return await message.reply(f'❗ {user.link}, У вас нет клана :(', disable_web_page_preview=True)
    clan = Clan(clan_id=clanuser.clan_id)
    try:
        clanwar = ClanWar(clan_id=clan.id)
    except:
        clanwar = None
    if len(arg) != 0 and arg[0].lower() in ['старт', 'начать']:
        if clanwar:
            return await message.reply(f'❗ {user.link}, война кланов уже начата!'
                                       '⚔️ Идёт подготовка', reply_markup=war_clan(clan_id=clan.id),
                                       disable_web_page_preview=True)
        if clanuser.status <= 1:
            return await message.reply(f'❗ {user.link},у вас низкий ранг для этого действия!',
                                       disable_web_page_preview=True)

        if clan.last_attack != None and (decimal.Decimal(time.time()) - clan.last_attack) < 3600 * 12:
            return await message.reply(
                f'🕑 {user.link}, Вы недавно уже атаковали, ващим товарищам нужно восстановиться!\n'
                f'Через: {timetostr(3600 * 12 + clan.last_attack - decimal.Decimal(time.time()))}',
                disable_web_page_preview=True)

        matchmaking_time = sql.execute(
            'SELECT AVG(EXTRACT(EPOCH FROM (end_time - start_time))) FROM ClanWarFind', fetchone=True)[0]

        matchmaking_time = matchmaking_time if matchmaking_time else 24 * 60 * 60

        try:
            ClanWarFind(clan_id=clan.id)
        except:
            ClanWarFind.find_to_war(clan.id, clan.name, clan.power, 'FINDING')
            await message.reply(
                f'{user.link},  информация по клановой войне:\n'
                '🛡 Идёт подбор противника...\n'
                '👥 Участников: 0\n'
                f'🕑 Приблизительное время подбора противника: {timetostr(matchmaking_time)}\n',
                reply_markup=war_clan_member(clan_id=clan.id),
                disable_web_page_preview=True)
            clanusers = \
                sql.execute(f"SELECT user_id FROM ClanUsers WHERE clan_id={clan.id}",
                            fetch=True)
            for user_id in clanusers:
                settings = Settings(user_id[0])
                if settings.clan_notifies:
                    with suppress(TelegramBadRequest):
                        await bot.send_message(chat_id=user_id[0], text=f"[КЛАН]\n"
                                                                        f'▶️ Игрок «{user.link}» начал клановую войну!\n"'
                                                                        '🔕 Для настройки уведомлений введите «Уведомления»')
                    await asyncio.sleep(0.5)
            return

        return await message.reply(
            f'{user.link},  информация по клановой войне:\n'
            '🛡 Идёт подбор противника...\n'
            '👥 Участников: 0\n'
            f'🕑 Приблизительное время подбора противника: {timetostr(matchmaking_time)}\n',
            reply_markup=war_clan_member(clan_id=clan.id),
            disable_web_page_preview=True)

    else:
        if clanwar:
            members = sql.select_data(table='WarParticipants', title='clan_id', name=clan.id)

            if clanwar.prepare:

                return await message.reply(
                    f'{user.link}, информация по клановой войне:\n'
                    f'⭐ Звезд: {clanwar.rating_first if clanwar.id_first == clan.id else clanwar.rating_second}\n'
                    f'🛡 Противник: «{clanwar.name_first if clanwar.name_first != clan.name else clanwar.name_second}»\n'
                    f'👥 Участников: {len(members)}\n'
                    f'🕑 До конца отборочного этапа: '
                    f'{unix_date(clanwar.time_war - timedelta(hours=3) - datetime.now())}\n',
                    reply_markup=war_clan(clan_id=clan.id),
                    disable_web_page_preview=True)
            else:
                return await message.reply(
                    f'{user.link}, информация по клановой войне:\n'
                    f'⭐ Звезд: {clanwar.rating_first if clanwar.id_first == clan.id else clanwar.rating_second}\n'
                    f'🛡 Противник: «{clanwar.name_first if clanwar.name_first != clan.name else clanwar.name_second}»\n'
                    f'👥 Участников: {len(members)}\n'
                    f'🕑 До конца Клановой войны: '
                    f'{unix_date(clanwar.time_war - datetime.now())}\n',
                    reply_markup=war_clan(clan_id=clan.id),
                    disable_web_page_preview=True)
        else:
            try:
                find = ClanWarFind(clan_id=clan.id)
            except:
                find = None

            if find is None:
                if clanuser.status <= 1:
                    return await message.reply(
                        f'{user.link}, клановая война не запущена !\n'
                        '💡 Вы можете обратиться к игрокам с высокими рангами с просьбой начать войну',
                        disable_web_page_preview=True)
                else:
                    return await message.reply(
                        f'{user.link}, клановая война не запущена !\n'
                        '💡 Для начала войны введите «Кв старт»',
                        disable_web_page_preview=True)
            else:

                matchmaking_time = sql.execute(
                    'SELECT AVG(EXTRACT(EPOCH FROM (end_time - start_time))) FROM ClanWarFind', fetchone=True)[0]

                matchmaking_time = matchmaking_time if matchmaking_time else 24 * 60 * 60

                return await message.reply(
                    f'{user.link},  информация по клановой войне:\n'
                    '🛡 Идёт подбор противника...\n'
                    '👥 Участников: 0\n'
                    f'🕑 Приблизительное время подбора противника: {timetostr(matchmaking_time)}\n',
                    reply_markup=war_clan_member(clan_id=clan.id),
                    disable_web_page_preview=True)


@router.callback_query(F.data.startswith('clanwar'))
@flags.throttling_key('default')
async def clanwar_action_call(callback_query: CallbackQuery):
    action, clan_id = callback_query.data.split(':')[1:]
    user = User(user=callback_query.from_user)
    try:
        clanuser = Clanuser(user_id=callback_query.from_user.id)
    except:
        if clanuser is None:
            return await callback_query.message.edit_text(f'? {user.link}, У вас нет клана :(',
                                                          disable_web_page_preview=True)
    clan = Clan(clan_id=clanuser.clan_id)
    try:
        clan_war_member = ClanWarMember(member_id=clanuser.user_id)
    except:
        clan_war_member = None
    try:
        clanwar = ClanWar(clan_id=clan.id)
    except:
        try:
            find = ClanWarFind(clan_id=clan.id)
        except:
            find = None
        if find is None:
            if clanuser.status <= 1:
                return await callback_query.message.edit_text(
                    f'{user.link}, клановая война не запущена !\n'
                    '💡 Вы можете обратиться к игрокам с высокими рангами с просьбой начать войну',
                    disable_web_page_preview=True)
            else:
                return await callback_query.message.edit_text(
                    f'{user.link}, клановая война не запущена !\n'
                    '💡 Для начала войны введите «Кв старт»',
                    disable_web_page_preview=True)
        else:
            matchmaking_time = sql.execute(
                'SELECT AVG(EXTRACT(EPOCH FROM (end_time - start_time))) FROM ClanWarFind', fetch=True)
            matchmaking_time = matchmaking_time[0][0] if matchmaking_time else 24 * 60 * 60
            return await callback_query.message.edit_text(
                f'{user.link},  информация по клановой войне:\n'
                '🛡 Идёт подбор противника...\n'
                '👥 Участников: 0\n'
                f'🕑 Приблизительное время подбора противника: {timetostr(matchmaking_time)}\n',
                reply_markup=war_clan_member(clan_id=clan.id),
                disable_web_page_preview=True)
    if not clanwar.prepare and not clan_war_member:
        return await callback_query.message.edit_text(f'{user.link}, Вы не успели пройти отборочный этап\n'
                                                      '💡 Нужно было сыграть как минимум 1 бой, чтобы участвовать в войне !',

                                                      disable_web_page_preview=True)
    if action == 'member':
        members = sql.select_data(table='WarParticipants', title='clan_id', name=clan_id)
        if not members:
            return await callback_query.message.edit_text(f'{user.link}, войне ещё нет участников \n'
                                                          '💡 Сыграйте как минимум 1 бой, чтобы участвовать в войне',
                                                          reply_markup=war_clan_info(clan_id=clan.id),
                                                          disable_web_page_preview=True)
        else:
            text = f"{user.link},  в клановой войне участвует {len(members)} человек::\n"
            for member in members:
                user_clan = User(id=member['member_id'])
                text += f'[👥] {user_clan.link}(<code>{user_clan.id}</code>) — 🎮 {member[4]}\n'
            return await callback_query.message.edit_text(text, reply_markup=war_clan_info(clan_id=clan.id),
                                                          disable_web_page_preview=True)
    elif action == 'info':

        members = sql.select_data(table='WarParticipants', title='clan_id', name=clan.id)
        if clanwar.prepare:
            return await callback_query.message.edit_text(
                f'{user.link}, информация по клановой войне:\n'
                f'⭐ Звезд: {clanwar.rating_first if clanwar.id_first == clan.id else clanwar.rating_second}\n'
                f'🛡 Противник: «{clanwar.name_first if clanwar.name_first != clan.name else clanwar.name_second}»\n'
                f'👥 Участников: {len(members)}\n'
                f'🕑 До конца отборочного этапа: '
                f'{unix_date(clanwar.time_war - timedelta(hours=3) - datetime.now())}\n',
                reply_markup=war_clan(clan_id=clan.id),
                disable_web_page_preview=True)
        else:
            return await callback_query.message.edit_text(
                f'{user.link}, информация по клановой войне:\n'
                f'⭐ Звезд: {clanwar.rating_first if clanwar.id_first == clan.id else clanwar.rating_second}\n'
                f'🛡 Противник: «{clanwar.name_first if clanwar.name_first != clan.name else clanwar.name_second}»\n'
                f'👥 Участников: {len(members)}\n'
                f'🕑 До конца Клановой войны: '
                f'{unix_date(clanwar.time_war - datetime.now())}\n',
                reply_markup=war_clan(clan_id=clan.id),
                disable_web_page_preview=True)


    elif action == 'attack':

        if not clan_war_member:
            ClanWarMember.insert_to_war(clanuser.user_id, clanuser.clan_id, clanwar.war_id, clanuser.power)
            clan_war_member = ClanWarMember(member_id=clanuser.user_id)
            result = QuestUser(user_id=user.id).update_progres(quest_ids=20, add_to_progresses=1)
            if result != '':
                await callback_query.message.answer(text=result.format(user=user.link), disable_web_page_preview=True)

        if clan_war_member.cooldown and time.time() - float(clan_war_member.cooldown) <= 300:
            return await callback_query.message.reply(
                f'🕑 Вы сможете снова вступить в бой через: {timetostr(float(clan_war_member.cooldown) + 300 - time.time())}',
                reply_markup=war_clan(clan_id=clan.id),
                disable_web_page_preview=True)
        oponent = sql.execute(
            f"SELECT user_id FROM ClanUsers WHERE clan_id={clanwar.id_first if clanwar.id_first != clan.id else clanwar.id_second} ORDER BY RANDOM() LIMIT 1",
            fetchone=True)
        try:
            weapon1 = Armory(armed=True, user_id=clanuser.user_id).weapon
        except:
            weapon1 = None
        try:
            weapon2 = Armory(armed=True, user_id=oponent['user_id']).weapon
        except:
            weapon2 = None
        armory_inv1 = ArmoryInv(clanuser.user_id)
        armory_inv2 = ArmoryInv(oponent['user_id'])
        user2 = User(id=oponent['user_id'])

        clan_war_member.edit('attacks', clan_war_member.attacks + 1)

        text = f'{user.link}, Вы напали на игрока «{user2.first_name}»:\n'
        count1 = 0
        count2 = 0
        for i in range(1, 4):
            damage_user1 = await attack_clan(weapon1, armory_inv1.min_damage, armory_inv1.max_damage)
            damage_user2 = await attack_clan(weapon2, armory_inv2.min_damage, armory_inv2.max_damage)
            if damage_user1 > damage_user2:
                count1 += 1
            else:
                count2 += 1
            text += f'Раунд {i}\n' \
                    f'{damage_user2} ⚔ {damage_user1}\n\n'
        clan_war_member.edit('cooldown', time.time())
        if count1 > count2:
            rating = random.randint(10, 20)
            clanuser.edit('rating', clanuser.rating + rating)
            if not clanwar.prepare:
                rating_clan = random.randint(100, 200)
                sql.execute(
                    f"UPDATE ClanWars SET {'rating_first' if clanwar.id_first == clan.id else 'rating_second'}="
                    f"{'rating_first' if clanwar.id_first == clan.id else 'rating_second'} + {rating_clan} "
                    f"WHERE war_id={clanwar.war_id} ", commit=True)
                text += f"⭐ Звезд: +{rating_clan}\n \n"
            return await callback_query.message.reply(f'{text}'
                                                      f'🎉 Ты победил в ⚔️дуэли со счетом {count1}:{count2}'
                                                      f'🏆 Рейтинг: +{rating}',
                                                      reply_markup=war_clan(clan_id=clan.id),
                                                      disable_web_page_preview=True)
        else:
            rating = random.randint(10, 20)
            clanuser.edit('rating', clanuser.rating - rating if clanuser.rating - rating > 0 else 0)
            return await callback_query.message.reply(f'{text}'
                                                      f'👎 Ты проиграл в ⚔️дуэли со счетом {count1}:{count2}'
                                                      f'🏆 Рейтинг: -{rating}',
                                                      reply_markup=war_clan(clan_id=clan.id),
                                                      disable_web_page_preview=True)
