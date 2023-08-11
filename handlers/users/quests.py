import random
from contextlib import suppress
from copy import deepcopy
from datetime import datetime, timedelta

from aiogram import flags
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery
from utils.main.cash import to_str4
from keyboard.main import quest_kb, quest_pag_kb
from utils.main.db import sql
from utils.main.users import User


def convert_datetime_to_str(dt):
    time_str = ""
    if dt.total_seconds() < 0:
        return "Можете сбросить квесты!"
    days = dt.days
    seconds = dt.seconds

    # Calculate the components of time
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if days > 0:
        time_str += f"{days}д:"
    if hours > 0:
        time_str += f"{hours:02}ч:"
    if minutes > 0:
        time_str += f"{minutes:02}м:"
    if seconds > 0:
        time_str += f"{seconds:02}с"

    return time_str


from utils.quests.main import QuestUser, quests_data, get_random_quests


def get_quests_for_pag(user_id):
    quests_per_page = 5
    all_quest_ids = []
    quests_commit = sql.execute(
        f"SELECT quest_id, under_quest_id FROM quests_commit WHERE user_id = {user_id} AND completed = True",
        fetch=True)
    first_elements = [lst[0] for lst in quests_commit]

    for index, quest_group in enumerate(quests_data.values(), start=1):
        for quest in quest_group:
            if index not in [lst[0] for lst in all_quest_ids] and index not in first_elements:
                all_quest_ids.append([index, quest['quest_id']])
    sublists = [all_quest_ids[i:i + quests_per_page] for i in range(0, len(all_quest_ids), quests_per_page)]
    return sublists


@flags.throttling_key('default')
async def quest_handler(message: Message):
    user_id = message.from_user.id
    questUser = QuestUser(user_id=user_id)
    user = User(id=user_id)
    text = f"📋 {user.link}, ваши задания на сегодня:\n\n"
    today_ids_quests = questUser.today_ids_quests
    for quest_id, under_quest_id in today_ids_quests:
        key = str(quest_id)
        if key not in quests_data:
            continue
        quest_list = quests_data[key]
        if under_quest_id <= 0 or under_quest_id > len(quest_list):
            continue
        quest_inf = quest_list[under_quest_id - 1]
        text += f"[{quest_inf['emoji']}] {quest_inf['title']}:\n" \
                f"▶️ Цель: {quest_inf['description']}\n"
        progress = questUser.get_progres(quest_id, under_quest_id)
        if not progress[1]:
            text += f"➖ {quest_inf['name_requirements']} {to_str4(progress[0])} {quest_inf['prefix_requirements']}\n\n"
        else:
            text += "✔ Выполнено\n\n"

    time_until_refresh = questUser.date_refresh - datetime.now()
    text += f"🕒 Новые квесты: {convert_datetime_to_str(time_until_refresh)}"
    if message.chat.type == 'private':
        await message.reply(text, reply_markup=quest_kb(user_id), disable_web_page_preview=True)
    else:
        await message.reply(text, disable_web_page_preview=True)


@flags.throttling_key('default')
async def quest_callback(callback: CallbackQuery):
    quest, action, user_id = callback.data.split('_')
    user_id = int(user_id)
    if user_id != callback.from_user.id:
        return await callback.answer(f'🤨 Убери свои шаловливые руки!')
    questUser = QuestUser(user_id=user_id)

    user = User(id=user_id)
    if action == 'reload':
        if (questUser.date_refresh - datetime.now()).total_seconds() > 0:
            return await callback.message.edit_text(
                f"📋 Новые квесты можно получить через {convert_datetime_to_str(questUser.date_refresh - datetime.now())}",
                reply_markup=quest_kb(user_id))
        now_date = datetime.now() + timedelta(hours=20)
        reg_date = now_date.strftime('%d-%m-%Y %H:%M:%S')
        cursor = sql.conn.cursor()
        # Fetch completed quest IDs for the specific user from quests_commit table
        cursor.execute("SELECT quest_id, under_quest_id FROM quests_commit WHERE user_id = %s AND completed = True",
                       (user_id,))
        quests_commit = cursor.fetchall()
        dontopen_quest = [[lst[0], lst[1] + 2] for lst in quests_commit]
        # Fetch today_ids_quests for the specific user from quests table
        cursor.execute("SELECT today_ids_quests FROM quests WHERE user_id = %s", (user_id,))
        today_ids_quests = cursor.fetchone()[0]
        # Extract the first element from each list in today_ids_quests
        first_elements = [lst[0] for lst in today_ids_quests]
        # Fetch all quest IDs from quests table
        all_quest_ids = get_random_quests()
        # Get quest IDs that are not completed and not already in today_ids_quests
        available_quests = []
        for index, quest_id in all_quest_ids:
            if index not in quests_commit and index not in first_elements:
                if index not in [lst[0] for lst in available_quests]:
                    if [index, quest_id] not in dontopen_quest:
                        available_quests.append([index, quest_id])

        # If available quests are less than max_quest_count, consider all of them
        selected_quests = random.sample(available_quests, min(3, len(available_quests)))
        cursor.execute("UPDATE quests SET today_ids_quests=%s ,date_refresh=%s WHERE user_id=%s ",
                       (selected_quests, reg_date, user_id,))
        sql.commit()

        text = f"📋 {user.link}, задания обновлены 👍🏼\n"
        for quest_id, under_quest_id in selected_quests:
            key = str(quest_id)
            if key not in quests_data:
                continue
            quest_list = quests_data[key]
            if under_quest_id <= 0 or under_quest_id > len(quest_list):
                continue
            quest_inf = quest_list[under_quest_id - 1]
            text += f"[{quest_inf['emoji']}] {quest_inf['title']}:\n" \
                    f"▶️ Цель: {quest_inf['description']}\n"
            progress = questUser.get_progres(quest_id, under_quest_id)
            if not progress[1]:
                text += f"➖ {quest_inf['name_requirements']} {to_str4(progress[0])} {quest_inf['prefix_requirements']}\n"
            else:
                text += "✔ Выполнено\n\n"

        time_until_refresh = now_date - datetime.now()
        text += f"🕒 Новые квесты: {convert_datetime_to_str(time_until_refresh)}"

        with suppress(TelegramBadRequest):
            return await callback.message.edit_text(text, reply_markup=quest_kb(user_id), disable_web_page_preview=True)
    elif action == 'advise':
        questUser = QuestUser(user_id=user_id)
        user = User(id=user_id)
        text = f"📋 {user.link}, ваши задания на сегодня:\n\n"
        today_ids_quests = questUser.today_ids_quests
        for quest_id, under_quest_id in today_ids_quests:
            key = str(quest_id)
            if key not in quests_data:
                continue
            quest_list = quests_data[key]
            if under_quest_id <= 0 or under_quest_id > len(quest_list):
                continue
            quest_inf = quest_list[under_quest_id - 1]
            text += f"[{quest_inf['emoji']}] {quest_inf['title']}:\n" \
                    f"▶️ Цель: {quest_inf['description']}\n"
            progress = questUser.get_progres(quest_id, under_quest_id)
            if not progress[1]:
                text += f"➖ {quest_inf['name_requirements']} {to_str4(progress[0])} {quest_inf['prefix_requirements']}\n"
                text += f"{quest_inf['advise']}\n\n"
            else:
                text += "✔ Выполнено\n\n"

        time_until_refresh = questUser.date_refresh - datetime.now()
        text += f"🕒 Новые квесты: {convert_datetime_to_str(time_until_refresh)}"

        with suppress(TelegramBadRequest):
            return await callback.message.edit_text(text, reply_markup=quest_kb(user_id), disable_web_page_preview=True)
    elif action == 'achiv':
        quests_commit = sql.execute(
            f"SELECT quest_id, under_quest_id FROM quests_commit WHERE user_id = {user_id} AND completed = True ORDER BY date_completed DESC LIMIT 3",
            fetch=True)

        text = f"🎯 {user.link},выполнено достижений: {len(quests_commit)} из {len(quests_data)}\n" \
               f"✅ Последние выполненные:\n"
        for index, quest_id in quests_commit:
            quest_inf = quests_data[str(index)][quest_id - 2]
            text += f"[{quest_inf['emoji']}] {quest_inf['title']} — «{quest_inf['description']}»\n"

        text += f"\n{random.choice(['🎳', '🎮', '🎯', '🧩', '🎲'])} Невыполненные достижения:\n"

        quests_data_pag = get_quests_for_pag(user_id)
        current_page_quests = quests_data_pag[0]
        for index, quest_id in current_page_quests:
            progress = questUser.get_progres(index, quest_id)
            quest_inf = quests_data[str(index)][progress[2] - 1]
            text += f"[{quest_inf['emoji']}] {quest_inf['title']} — «{quest_inf['description']}»\n" \
                    f"➖ {quest_inf['name_requirements']} {to_str4(progress[0])} {quest_inf['prefix_requirements']}\n"
        total_pages = len(quests_data_pag)
        text += f"\n▶️ Страница 1 из {total_pages}"
        with suppress(TelegramBadRequest):
            # text += f"🕒 Новые квесты: {convert_datetime_to_str(questUser.date_refresh - datetime.now())}"
            return await callback.message.edit_text(text,
                                                    reply_markup=quest_pag_kb(user_id, 1, total_pages),
                                                    disable_web_page_preview=True)


@flags.throttling_key('default')
async def quest_pagination_callback(callback: CallbackQuery):
    action, page, user_id = callback.data.split('_')[2:]

    page = int(page)
    user_id = int(user_id)
    if user_id != callback.from_user.id:
        return await callback.answer(f'🤨 Убери свои шаловливые руки!')
    questUser = QuestUser(user_id=user_id)
    user = User(id=user_id)
    quests_commit = sql.execute(
        f"SELECT quest_id, under_quest_id FROM quests_commit WHERE user_id = {user_id} AND completed = True ORDER BY date_completed DESC LIMIT 3",
        fetch=True)
    text = f"🎯 {user.link},выполнено достижений: {len(quests_commit)} из {len(quests_data)}\n" \
           f"✅ Последние выполненные:\n"
    for index, quest_id in quests_commit:
        quest_inf = quests_data[str(index)][quest_id - 2]
        text += f"[{quest_inf['emoji']}] {quest_inf['title']} — «{quest_inf['description']}»\n"

    text += f"\n{random.choice(['🎳', '🎮', '🎯', '🧩', '🎲'])} Невыполненные достижения:\n"
    quests_data_pag = get_quests_for_pag(user_id)
    current_page_quests = quests_data_pag[page - 1]
    for index, quest_id in current_page_quests:
        progress = questUser.get_progres(index, quest_id)
        quest_inf = quests_data[str(index)][progress[2] - 1]
        text += f"[{quest_inf['emoji']}] {quest_inf['title']} — «{quest_inf['description']}»\n" \
                f"➖ {quest_inf['name_requirements']} {to_str4(progress[0])} {quest_inf['prefix_requirements']}\n"

    # text += f"🕒 Новые квесты: {convert_datetime_to_str(questUser.date_refresh - datetime.now())}"
    total_pages = len(quests_data_pag)
    text += f"\n▶️ Страница {page} из {total_pages}"
    if action == 'prev':
        with suppress(TelegramBadRequest):
            return await callback.message.edit_text(text,
                                                    reply_markup=quest_pag_kb(user_id, page, total_pages),
                                                    disable_web_page_preview=True)
    if action == 'next':
        with suppress(TelegramBadRequest):
            return await callback.message.edit_text(text,
                                                    reply_markup=quest_pag_kb(user_id, page, total_pages),
                                                    disable_web_page_preview=True)
