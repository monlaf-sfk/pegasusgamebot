from datetime import datetime, timedelta
import decimal
import time

from aiogram import flags, Router, F, Bot
from aiogram.types import Message

from config import bot_name
from filters.triggers import Trigger

from utils.clan.clan import Clanuser, Clan
from utils.clan.clanwar import ClanWar, ClanWarFind
from utils.main.donates import to_str as unix_date
from utils.main.db import sql, timetostr
from utils.main.users import User

router = Router()
router.message.filter(F.chat.type.in_({"group", "supergroup"}))


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
                                       '⚔️ Идёт подготовка',
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
            'SELECT AVG(EXTRACT(EPOCH FROM (end_time - start_time))) FROM ClanWarFind', fetch=True)
        matchmaking_time = matchmaking_time[0][0] if matchmaking_time else 24 * 60 * 60

        try:
            ClanWarFind(clan_id=clan.id)
        except:
            ClanWarFind.find_to_war(clan.id, clan.name, clan.power, 'FINDING')
            return await message.reply(
                f'{user.link},  информация по клановой войне:\n'
                '🛡 Идёт подбор противника...\n'
                '👥 Участников: 0\n'
                f'🕑 Приблизительное время подбора противника: {timetostr(matchmaking_time)}\n',

                disable_web_page_preview=True)

        return await message.reply(
            f'{user.link},  информация по клановой войне:\n'
            '🛡 Идёт подбор противника...\n'
            '👥 Участников: 0\n'
            f'🕑 Приблизительное время подбора противника: {timetostr(matchmaking_time)}\n',

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

                    disable_web_page_preview=True)
            else:
                return await message.reply(
                    f'{user.link}, информация по клановой войне:\n'
                    f'⭐ Звезд: {clanwar.rating_first if clanwar.id_first == clan.id else clanwar.rating_second}\n'
                    f'🛡 Противник: «{clanwar.name_first if clanwar.name_first != clan.name else clanwar.name_second}»\n'
                    f'👥 Участников: {len(members)}\n'
                    f'🕑 До конца Клановой войны: '
                    f'{unix_date(clanwar.time_war - datetime.now())}\n',

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
                    'SELECT AVG(EXTRACT(EPOCH FROM (end_time - start_time))) FROM ClanWarFind', fetch=True)
                matchmaking_time = matchmaking_time[0][0] if matchmaking_time else 24 * 60 * 60

                return await message.reply(
                    f'{user.link},  информация по клановой войне:\n'
                    '🛡 Идёт подбор противника...\n'
                    '👥 Участников: 0\n'
                    f'🕑 Приблизительное время подбора противника: {timetostr(matchmaking_time)}\n',

                    disable_web_page_preview=True)
