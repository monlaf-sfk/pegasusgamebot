import asyncio
from contextlib import suppress
from datetime import timedelta, datetime

from aiogram import flags, Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message

from utils.main.cash import to_str
from utils.main.db import sql
from utils.main.donates import to_str as unix_date
from config import bot_name
from filters.triggers import Trigger
from utils.clan.clan import Clanuser, Clan
from utils.clan.clan_rob import ClanRob
from utils.items.items import items_rob

from utils.main.users import User, Settings

router = Router()

name_robs = {
    1: {
        'emoji': "🏪",
        'name': "Магазин",
        'min_member': 2,
        'need_robs': 0,
        'income': 16_000_000,
        'time_prepare': '03:00:00',
        'plan': {
            1: {'name': "☀ Нападение днём",
                'subjects': [1, 3, 5, 7, 9]
                },
            2: {'name': "🌠 Нападение ночью",
                'subjects': [2, 4, 6, 8, 10]
                }
        }
    },
    2: {
        'emoji': "🏘",
        'name': "Дом/Квартира",
        'min_member': 4,
        'need_robs': 1,
        'income': 43_000_000,
        'time_prepare': '03:30:00',
        'hours': 3,
        'plan': {
            1: {'name': "🏡 Ограбление дома",
                'subjects': [1, 3, 5, 7, 9]
                },
            2: {'name': "🏙 Ограбление квартиры",
                'subjects': [2, 4, 6, 8, 10]
                }
        }
    },
    3: {
        'emoji': "🏬",
        'name': "Ювелирный магазин",
        'min_member': 8,
        'need_robs': 4,
        'income': 87_000_000,
        'time_prepare': '04:00:00',

        'plan': {
            1: {'name': "☀ Нападение днём",
                'subjects': [1, 3, 5, 7, 9]
                },
            2: {'name': "🌠 Нападение ночью",
                'subjects': [2, 4, 6, 8, 10]
                }
        }
    },
    4: {
        'emoji': "🏙",
        'name': "Коттедж",
        'min_member': 16,
        'need_robs': 10,
        'income': 137_000_000,
        'time_prepare': '04:30:00',
        'plan': {
            1: {'name': "☀ Нападение днём",
                'subjects': [1, 3, 5, 7, 9]
                },
            2: {'name': "🌠 Нападение ночью",
                'subjects': [2, 4, 6, 8, 10]
                }
        },
    }
}


def opened_robs(count_robs):
    text = "{user}, доступные ограбления:\n"
    for index, rob_id in enumerate(name_robs, start=1):
        rob = name_robs[rob_id]
        if rob['need_robs'] <= count_robs:
            text += f"{index}. {rob['name']} — 👥 {rob['min_member']}\n" \
                    f"   {rob['emoji']} Прибыль: ≈{to_str(rob['income'])}\n"
    text += "💸 - стоимость подготовки | 👥 - минимальное количество участников\n" \
            "▶️ Введите «Ограбление [номер]» для начала 👍🏼\n"
    return text


@router.message(Trigger(["ограбление"]))
@flags.throttling_key('default')
async def clan_rob_handler(message: Message, bot: Bot):
    arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[
        0].lower() else message.text.split()[2:]

    user = User(id=message.from_user.id)
    try:
        clanuser = Clanuser(user_id=message.from_user.id)
    except:
        return await message.reply(f'? {user.link}, У вас нет клана :(', disable_web_page_preview=True)
    try:
        clan_rob = ClanRob(clan_id=clanuser.clan_id)
    except:
        clan_rob = None
    clan = Clan(clan_id=clanuser.clan_id)
    if len(arg) == 0 and clan_rob:
        count = sql.execute(f"SELECT COUNT(*) AS count FROM ClanUsers WHERE rob_involved=True AND clan_id={clan.id}",
                            fetchone=True)[0]
        if clan_rob.prepare and clan_rob.plan_rob != 0:
            return await message.reply(
                f'{user.link}, информация об ограблении «{name_robs[clan_rob.index_rob]["name"]}»:\n'
                f"📋 План: {name_robs[clan_rob.index_rob]['plan'][clan_rob.plan_rob]['name']}\n"
                f'👥 Участников: {count}/{name_robs[clan_rob.index_rob]["min_member"]}\n'
                f'{"✅ Вы участвуете в ограблении!" if clanuser.rob_involved else "❌ Ты не допущен к ограблению, приобрети все требуемые предметы"}\n'
                f'🕐 Время на подготовку: {unix_date(clan_rob.time_rob - datetime.now())}\n',
                disable_web_page_preview=True)
        elif clan_rob.prepare and clan_rob.plan_rob == 0:
            return await message.reply(
                f'{user.link}, информация об ограблении «{name_robs[clan_rob.index_rob]["name"]}»:\n'
                f"📋 План: не выбран\n"
                f'👥 Участников: {count}/{name_robs[clan_rob.index_rob]["min_member"]}\n'
                f'{"✅ Вы участвуете в ограблении!" if clanuser.rob_involved else "❌ Ты не допущен к ограблению, приобрети все требуемые предметы"}\n'
                f'🕐 Время на подготовку: {unix_date(clan_rob.time_rob - datetime.now())}\n',
                disable_web_page_preview=True)
        elif not clan_rob.prepare and not clan_rob.time_rob:
            return await message.reply(
                f'{user.link}, информация об ограблении «{name_robs[clan_rob.index_rob]["name"]}»:\n'
                f"📋 План: {name_robs[clan_rob.index_rob]['plan'][clan_rob.plan_rob]['name']}\n"
                f'👥 Участников: {count}/{name_robs[clan_rob.index_rob]["min_member"]}\n'
                f'{"✅ Вы участвуете в ограблении!" if clanuser.rob_involved else "❌ Ты не допущен к ограблению, приобрети все требуемые предметы"}\n'
                f'🕐 Подготовка завершена, можно начинать ограбление\n', disable_web_page_preview=True)
        elif not clan_rob.prepare and clan_rob.time_rob:
            return await message.reply(
                f'{user.link}, информация об ограблении «{name_robs[clan_rob.index_rob]["name"]}»:\n'
                f"📋 План: {name_robs[clan_rob.index_rob]['plan'][clan_rob.plan_rob]['name']}\n"
                f'👥 Участников: {count}/{name_robs[clan_rob.index_rob]["min_member"]}\n'
                f'{"✅ Вы участвуете в ограблении!" if clanuser.rob_involved else "❌ Ты не допущен к ограблению, приобрети все требуемые предметы"}\n'
                f'💵 Награблено валюты: {to_str(clan_rob.balance)}\n'
                f'🕙 Завершение через {unix_date(clan_rob.time_rob - datetime.now())}\n', disable_web_page_preview=True)


    elif len(arg) == 1 and not clan_rob and arg[0].isdigit():
        if clanuser.status != 2:
            return await message.reply(f'❗ {user.link}, у Вас недостаточно прав для старта ограбления ☹️',
                                       disable_web_page_preview=True)
        try:
            index_rob = int(arg[0])
            robs = name_robs[index_rob]
        except KeyError:
            return await message.reply(opened_robs(clan.count_robs).format(user=user.link),
                                       disable_web_page_preview=True)
        if robs['need_robs'] > clan.count_robs:
            return await message.reply(opened_robs(clan.count_robs).format(user=user.link),
                                       disable_web_page_preview=True)
        ClanRob.create_rob(clan.id, index_rob, robs['time_prepare'])
        text = '\n'.join([f"{index}. {plan['name']}" for index, plan in robs['plan'].items()])
        await message.reply(f"{user.link}, Вы начали ограбление «{robs['name']}»:\n"
                            f"🕐 Время на подготовку: {robs['time_prepare']}\n"
                            f"🔫 Способы прохождения: \n{text}\n"
                            f"▶️ Выберите план с помощью команды «Ограбление план [номер]» ",
                            disable_web_page_preview=True)
        clanusers = \
            sql.execute(f"SELECT user_id FROM ClanUsers WHERE clan_id={clan.id}",
                        fetch=True)
        for user_id in clanusers:
            settings = Settings(user_id[0])
            if settings.clan_notifies:
                with suppress(TelegramBadRequest):
                    await bot.send_message(chat_id=user_id[0], text=f"""[КЛАН]
▶️Началась подготовка к ограблению! Успей принять участие!
📃 Для участия приобретите все требуемые предметы: команда «Шоп»
🔕 Для настройки уведомлений введите «Уведомления»""")
                await asyncio.sleep(0.5)
    elif not clan_rob:
        return await message.reply(opened_robs(clan.count_robs).format(user=user.link), disable_web_page_preview=True)
    elif len(arg) == 0 and clan_rob.plan_rob == 0:
        if clanuser.status != 2:
            return await message.reply(f'❗ {user.link}, у Вас недостаточно прав для старта ограбления ☹️',
                                       disable_web_page_preview=True)
        text = '\n'.join([f"{index}. {plan['name']}" for index, plan in name_robs[clan_rob.index_rob]['plan'].items()])

        return await message.reply(f"{user.link}, доступные способы прохождения:\n"
                                   + text + "\n💡 Для выбора плана введите «Ограбление план [номер]»",
                                   disable_web_page_preview=True)
    elif arg[0].lower() == "старт":
        if clanuser.status != 2:
            return await message.reply(f'❗ {user.link}, у Вас недостаточно прав для старта ограбления ☹️',
                                       disable_web_page_preview=True)
        count = \
            sql.execute(f"SELECT COUNT(*) AS count FROM ClanUsers WHERE rob_involved=True AND clan_id={clan.id}",
                        fetchone=True)[0]
        if clan_rob.prepare and clan_rob.plan_rob == 0:
            return await message.reply(f'❗ {user.link}, начать ограбление можно '
                                       f'после выбора плана ограбления 😩'
                                       f'\n💡 Для выбора плана введите «Ограбление план [номер]»',
                                       disable_web_page_preview=True)
        if count < name_robs[clan_rob.index_rob]["min_member"]:
            return await message.reply(
                f"{user.link}, в ограблении требуется минимум {name_robs[clan_rob.index_rob]['min_member']} игрока 😔\n"
                f"👥 Участников в данный момент: {count}\n"
                "▶️ Игроки для участия в ограблении должны приобрести все требуемые предметы! Команда: «Шоп»\n",
                disable_web_page_preview=True)

        if clan_rob.prepare:
            return await message.reply(f"{user.link}, начать ограбление можно после подготовки!\n"
                                       f"🕘 Конец подготовки через: {unix_date(clan_rob.time_rob - datetime.now())}\n"
                                       f"👥 Количество участников: {count}\n", disable_web_page_preview=True)

        if not clan_rob.prepare and clan_rob.time_rob:
            return await message.reply(f"{user.link}, ограбление уже запущено 👍🏻\n"
                                       "▶️ Следите за текущим прогрессом с помощью команды «Ограбление»",
                                       disable_web_page_preview=True)
        dt = datetime.now()
        time_rob = dt + timedelta(hours=1)
        clan_rob.edit("time_rob", time_rob.strftime('%d-%m-%Y %H:%M:%S'))
        await message.reply(f"{user.link}, ограбление началось!\n"
                            "🕙 Ограбление будет идти примерно 59м 59с\n"
                            "💬 Следить за ходом событий можно с помощью команд «Ограбление»\n",
                            disable_web_page_preview=True)
        clanusers = \
            sql.execute(f"SELECT user_id FROM ClanUsers WHERE rob_involved=True AND clan_id={clan.id}",
                        fetch=True)
        for user_id in clanusers:
            settings = Settings(user_id[0])
            if settings.clan_notifies:
                with suppress(TelegramBadRequest):
                    await bot.send_message(chat_id=user_id[0], text=f"""[КЛАН]
▶️ Подготовка к ограблению завершена! Игрок «{user.link}» начал ограбление ☺️

💬 Следить за ходом событий можно с помощью команд «Ограбление»
🔕 Для настройки уведомлений введите «Уведомления»""")
                await asyncio.sleep(0.5)

    elif arg[0].lower() == "план":
        if clanuser.status != 2:
            return await message.reply(f'❗ {user.link}, у Вас недостаточно прав для старта ограбления ☹️',
                                       disable_web_page_preview=True)
        if clan_rob.plan_rob != 0:
            return await message.reply(
                f"{user.link}, выбран план «{name_robs[clan_rob.index_rob]['plan'][clan_rob.plan_rob]['name']}» 👍🏼",
                disable_web_page_preview=True)
        try:
            plan_rob_ind = int(arg[1])
            plan_rob = name_robs[clan_rob.index_rob]['plan'][plan_rob_ind]
        except (IndexError, KeyError):
            text = '\n'.join(
                [f"{index}. {plan['name']}" for index, plan in name_robs[clan_rob.index_rob]['plan'].items()])

            return await message.reply(f"{user.link}, доступные способы прохождения:\n"
                                       + text + "\n💡 Для выбора плана введите «Ограбление план [номер]»",
                                       disable_web_page_preview=True)
        text = ''
        numbers_emoji = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']
        for index, item_id in enumerate(plan_rob['subjects'], start=1):
            emoji = ''.join(numbers_emoji[int(i)] for i in str(index))
            item = items_rob[item_id]
            text += f'{emoji} {item["emoji"]} {item["name"]}\n'
        clan_rob.edit('plan_rob', plan_rob_ind)
        return await message.reply(
            f"{user.link}, Вы выбрали план №{plan_rob_ind} ({plan_rob['name']})\n"
            f"📋 Требуемые предметы:\n"
            + text + "\n❔ Чтобы участвовать в ограблении, игроки должны купить все эти предметы!",
            disable_web_page_preview=True)
