import json
import os

import aiosqlite

DATABASE_FILE = 'users_state.db'


async def create_table():
    async with aiosqlite.connect(DATABASE_FILE) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT,
                stategroup TEXT ,
                state TEXT ,
                data TEXT,
                UNIQUE(user_id, stategroup)
            )
        ''')
        await db.commit()


async def set_user_data(user_id, stategroup, state, data):
    await create_table()
    async with aiosqlite.connect(DATABASE_FILE) as db:
        await db.execute(
            "INSERT OR REPLACE INTO users (user_id, state, stategroup, data) VALUES (?, ?, ?, ?)",
            (user_id, state, stategroup, json.dumps(data))
        )
        await db.commit()


async def get_user_data(user_id, state, stategroup):
    await create_table()
    async with aiosqlite.connect(DATABASE_FILE) as db:
        cursor = await db.execute(
            "SELECT data FROM users WHERE user_id = ? AND state = ? AND stategroup = ?",
            (user_id, state, stategroup)
        )
        data = await cursor.fetchone()
        if data:
            return json.loads(data[0])
        return {}


def str_to_dict(string):
    # remove the curly braces from the string
    string = string.strip('{}')

    # split the string into key-value pairs
    pairs = string.split(', ')

    # use a dictionary comprehension to create
    # the dictionary, converting the values to
    # integers and removing the quotes from the keys
    return {key[1:-2]: int(value) for key, value in (pair.split(': ') for pair in pairs)}


async def get_user_state_data(user_id, stategroup):
    await create_table()
    async with aiosqlite.connect(DATABASE_FILE) as db:
        cursor = await db.execute(
            "SELECT state, data FROM users WHERE user_id = ? AND stategroup = ?",
            (user_id, stategroup)
        )

        data = await cursor.fetchone()

        if data:
            state, data_value = data  # Unpack the fetched row into separate variables
            return {"state": state, "data": json.loads(data_value)
                    }
        return None


async def update_state_for_user(user_id, new_state, old_state, stategroup):
    await create_table()
    async with aiosqlite.connect(DATABASE_FILE) as db:
        await db.execute(
            "UPDATE users SET state = ? WHERE user_id = ? AND state = ? AND stategroup = ?",
            (new_state, user_id, old_state, stategroup)
        )

        await db.commit()


async def update_data_for_group_state(user_id, new_data, state, stategroup):
    await create_table()
    async with aiosqlite.connect(DATABASE_FILE) as db:
        await db.execute(
            "UPDATE users SET data = ? WHERE user_id = ? AND state = ? AND stategroup = ?",
            (json.dumps(new_data), user_id, state, stategroup)
        )
        await db.commit()


async def update_data_and_state(user_id, new_data, state, stategroup):
    await create_table()
    async with aiosqlite.connect(DATABASE_FILE) as db:
        await db.execute(
            "UPDATE users SET data = ? , state = ? WHERE user_id = ? AND stategroup = ?",
            (json.dumps(new_data), state, user_id, stategroup)
        )
        await db.commit()


async def delete_user_state(user_id, state, stategroup):
    async with aiosqlite.connect(DATABASE_FILE) as db:
        await db.execute(
            "DELETE FROM users WHERE user_id = ? AND stategroup = ?",
            (int(user_id), stategroup)
        )
        await db.commit()
