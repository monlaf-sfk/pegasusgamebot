import decimal
import json
import random
from datetime import datetime, timedelta

from utils.main.cash import to_str4
from utils.main.db import sql


class QuestUser:
    def __init__(self, user_id: int = None):
        self.source = sql.select_data(user_id, 'user_id', True, 'quests')
        if self.source is None:
            self.source = QuestUser.create(user_id)
        self.user_id: int = self.source[0]
        self.date_refresh: datetime = self.source[1]
        self.today_ids_quests: list = self.source[2]

    def get_progres(self, quest_id, under_quest_id):

        progress = sql.execute(
            f'SELECT progress,completed,under_quest_id FROM quests_commit WHERE user_id = {self.user_id} AND quest_id = {quest_id} ORDER BY under_quest_id DESC LIMIT 1',
            fetchone=True)
        if not progress:
            data = [(quest_id, under_quest_id, self.user_id, False, 0, None, None)]
            placeholders = ', '.join(['%s'] * len(data[0]))
            sql.cursor.execute(f"INSERT INTO quests_commit VALUES (DEFAULT, {placeholders})", data[0])
            sql.commit()
            progress = [0, False, under_quest_id]
        return progress

    def update_progres(self, quest_ids, add_to_progresses):
        text = ''
        if isinstance(quest_ids, int):
            quest_ids = [quest_ids]
        if isinstance(add_to_progresses, int):
            add_to_progresses = [add_to_progresses]
        for quest_id, add_to_progress in zip(quest_ids, add_to_progresses):
            result = sql.execute(
                f'SELECT progress,under_quest_id,completed FROM quests_commit WHERE user_id = {self.user_id} AND quest_id = {quest_id} ORDER BY under_quest_id DESC LIMIT 1',
                fetchone=True)

            if not result:
                data = [(quest_id, 1, self.user_id, False, add_to_progress, None, None)]
                placeholders = ', '.join(['%s'] * len(data[0]))
                sql.cursor.execute(f"INSERT INTO quests_commit VALUES (DEFAULT, {placeholders})", data[0])
                sql.commit()
                result = [0, 1, False]
            else:
                if result[2]:
                    continue
                sql.execute(
                    f'UPDATE quests_commit SET progress= progress + {add_to_progress} WHERE user_id = {self.user_id} AND quest_id = {quest_id} AND under_quest_id={result[1]}',
                    commit=True)

            quest_inf = quests_data[str(quest_id)][result[1] - 1]
            quest_last_id = quests_data[str(quest_id)][-1]['quest_id']
            if quest_inf['requirements'] <= result[0] + add_to_progress:
                if result[1] == quest_last_id:
                    sql.execute(
                        f'UPDATE quests_commit SET under_quest_id = under_quest_id+1,progress=0,completed = TRUE,last_value=NULL,'
                        f"date_completed='{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}' WHERE user_id = {self.user_id} AND quest_id = {quest_id} AND under_quest_id={result[1]}",
                        commit=True)
                    if text != "":
                        text += f"\nДостижение «{quest_inf['title']}» выполнено!  🙂\n" \
                                f"{quest_inf['emoji_reward']} Награда: {to_str4(quest_inf['reward_count'])}{quest_inf['prefix_reward']}\n"
                    else:
                        text = "{user}, " \
                               f"достижение «{quest_inf['title']}» выполнено!  🙂\n" \
                               f"{quest_inf['emoji_reward']} Награда: {to_str4(quest_inf['reward_count'])}{quest_inf['prefix_reward']}\n"
                else:
                    original_list = self.today_ids_quests
                    for sublist in original_list:
                        if sublist == [quest_id, result[1]]:
                            sublist[1] = result[1] + 1
                    sql.cursor.execute('UPDATE quests SET today_ids_quests = %s WHERE user_id = %s',
                                       (original_list, self.user_id))
                    sql.execute(
                        f'UPDATE quests_commit SET under_quest_id = under_quest_id+1,progress=0 WHERE user_id = {self.user_id} AND quest_id = {quest_id} AND under_quest_id={result[1]}',
                        commit=True)
                    if text != "":
                        text += f"\nДостижение «{quest_inf['title']}» выполнено! [{result[1]} из {quest_last_id}] 🙂\n" \
                                f"{quest_inf['emoji_reward']} Награда: {to_str4(quest_inf['reward_count'])}{quest_inf['prefix_reward']}\n" \
                                f"{quest_inf['emoji']} Следующая цель: {quests_data[str(quest_id)][result[1]]['description']}"
                    else:
                        text = "{user}, " \
                               f"достижение «{quest_inf['title']}» выполнено! [{result[1]} из {quest_last_id}] 🙂\n" \
                               f"{quest_inf['emoji_reward']} Награда: {to_str4(quest_inf['reward_count'])}{quest_inf['prefix_reward']}\n" \
                               f"{quest_inf['emoji']} Следующая цель: {quests_data[str(quest_id)][result[1]]['description']}"
                if quest_inf['type_reward'] == "money":
                    sql.execute(
                        f'UPDATE users SET balance = balance + {quest_inf["reward_count"]} WHERE id = {self.user_id} ',
                        commit=True)
                elif quest_inf['type_reward'] == "bitcoin":
                    sql.execute(
                        f'UPDATE users SET bitcoins = bitcoins + {quest_inf["reward_count"]} WHERE id = {self.user_id} ',
                        commit=True)
                elif quest_inf['type_reward'] == "case":
                    ...
        return text

    def check_progres(self, quest_ids, progresses):
        text = ''
        if isinstance(quest_ids, int):
            quest_ids = [quest_ids]
        if isinstance(progresses, (int, float, decimal.Decimal)):
            progresses = [progresses]
        for quest_id, add_to_progress in zip(quest_ids, progresses):
            result = sql.execute(
                f'SELECT progress,under_quest_id,completed FROM quests_commit WHERE user_id = {self.user_id} AND quest_id = {quest_id} ORDER BY under_quest_id DESC LIMIT 1',
                fetchone=True)

            if not result:
                data = [(quest_id, 1, self.user_id, False, add_to_progress, None, None)]
                placeholders = ', '.join(['%s'] * len(data[0]))
                sql.cursor.execute(f"INSERT INTO quests_commit VALUES (DEFAULT, {placeholders})", data[0])
                sql.commit()
                result = [0, 1, False]
            else:
                if result[2]:
                    continue
                sql.execute(
                    f'UPDATE quests_commit SET progress= {add_to_progress} WHERE user_id = {self.user_id} AND quest_id = {quest_id} AND under_quest_id={result[1]}',
                    commit=True)
            quest_inf = quests_data[str(quest_id)][result[1] - 1]
            quest_last_id = quests_data[str(quest_id)][-1]['quest_id']
            if quest_inf['requirements'] <= add_to_progress:
                if result[1] == quest_last_id:

                    sql.execute(
                        f'UPDATE quests_commit SET under_quest_id = under_quest_id+1,progress=0,completed = TRUE,last_value=NULL,'
                        f"date_completed='{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}' WHERE user_id = {self.user_id} AND quest_id = {quest_id} AND under_quest_id={result[1]}",
                        commit=True)
                    if text != "":
                        text += f"\nДостижение «{quest_inf['title']}» выполнено!  🙂\n" \
                                f"{quest_inf['emoji_reward']} Награда: {to_str4(quest_inf['reward_count'])}{quest_inf['prefix_reward']}\n"
                    else:
                        text = "{user}, " \
                               f"достижение «{quest_inf['title']}» выполнено!  🙂\n" \
                               f"{quest_inf['emoji_reward']} Награда: {to_str4(quest_inf['reward_count'])}{quest_inf['prefix_reward']}\n"
                else:
                    original_list = self.today_ids_quests
                    for sublist in original_list:
                        if sublist == [quest_id, result[1]]:
                            sublist[1] = result[1] + 1
                    sql.cursor.execute('UPDATE quests SET today_ids_quests = %s WHERE user_id = %s',
                                       (original_list, self.user_id))
                    sql.execute(
                        f'UPDATE quests_commit SET under_quest_id = under_quest_id+1,progress=0 WHERE user_id = {self.user_id} AND quest_id = {quest_id} AND under_quest_id={result[1]}',
                        commit=True)
                    if text != "":
                        text += f"\nДостижение «{quest_inf['title']}» выполнено! [{result[1]} из {quest_last_id}] 🙂\n" \
                                f"{quest_inf['emoji_reward']} Награда: {to_str4(quest_inf['reward_count'])}{quest_inf['prefix_reward']}\n" \
                                f"{quest_inf['emoji']} Следующая цель: {quests_data[str(quest_id)][result[1]]['description']}"
                    else:
                        text = "{user}, " \
                               f"достижение «{quest_inf['title']}» выполнено! [{result[1]} из {quest_last_id}] 🙂\n" \
                               f"{quest_inf['emoji_reward']} Награда: {to_str4(quest_inf['reward_count'])}{quest_inf['prefix_reward']}\n" \
                               f"{quest_inf['emoji']} Следующая цель: {quests_data[str(quest_id)][result[1]]['description']}"
                if quest_inf['type_reward'] == "money":
                    sql.execute(
                        f'UPDATE users SET balance = balance + {quest_inf["reward_count"]} WHERE id = {self.user_id} ',
                        commit=True)
                elif quest_inf['type_reward'] == "bitcoin":
                    sql.execute(
                        f'UPDATE users SET bitcoins = bitcoins + {quest_inf["reward_count"]} WHERE id = {self.user_id} ',
                        commit=True)
                elif quest_inf['type_reward'] == "case":
                    ...
        return text

    def edit(self, name, value, attr=True):
        if attr:
            setattr(self, name, value)
        sql.edit_data('user_id', self.user_id, name, value, 'quests')
        return value

    @staticmethod
    def create(user_id: int):
        now_date = datetime.now() + timedelta(hours=20)
        reg_date = now_date.strftime('%d-%m-%Y %H:%M:%S')
        cursor = sql.conn.cursor()

        # Fetch completed quest IDs for the specific user from quests_commit tabl
        cursor.execute("SELECT quest_id, under_quest_id FROM quests_commit WHERE user_id = %s AND completed = True",
                       (user_id,))
        quests_commit = cursor.fetchall()
        dontopen_quest = [[lst[0], lst[1] + 2] for lst in quests_commit]
        # Fetch today_ids_quests for the specific user from quests table

        # Extract the first element from each list in today_ids_quests
        all_quest_ids = get_random_quests()
        available_quests = []
        # Get quest IDs that are not completed and not already in today_ids_quests
        for index, quest_id in all_quest_ids:
            if [index, quest_id] not in quests_commit:
                if index not in [lst[0] for lst in available_quests]:
                    if [index, quest_id] not in dontopen_quest:
                        available_quests.append([index, quest_id])

        # If available quests are less than max_quest_count, consider all of them
        selected_quests = random.sample(available_quests, min(3, len(available_quests)))

        res = (user_id, reg_date, selected_quests)
        query = "INSERT INTO quests (user_id, date_refresh, today_ids_quests) VALUES (%s,%s,%s)"

        cursor.execute(query, res)
        sql.commit()

        return (user_id, now_date, selected_quests)


def get_random_quests():
    all_quest_ids = []
    for index, quest_group in enumerate(quests_data.values(), start=1):
        for quest in quest_group:
            if index not in all_quest_ids:
                all_quest_ids.append([index, quest['quest_id']])
    return all_quest_ids


def load_quests_from_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        quests_data = json.load(file)

    return quests_data['quests']


import os

dir_path = os.path.dirname(os.path.realpath(__file__))
quests_data = load_quests_from_json(dir_path + '/' + 'quests.json')
