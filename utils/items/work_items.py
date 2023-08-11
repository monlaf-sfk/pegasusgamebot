from utils.main.db import sql


def get_workitems_count(works_item_id, user_id):
    count = sql.execute(f"SELECT count FROM user_work_items WHERE user_id={user_id} AND works_item_id={works_item_id}",
                        fetchone=True)
    return count['count'] if count else None


def fetch_all_workitems_counts(user_id):
    work_counts = sql.execute(f"SELECT works_item_id, count FROM user_work_items WHERE user_id={user_id}", fetch=True)

    if work_counts is None:
        return {}  # Return an empty dictionary if no records are found
    return {work_count['works_item_id']: work_count['count'] for work_count in work_counts}


def set_workitems_count(works_item_id, user_id, count):
    existing_count = get_workitems_count(works_item_id, user_id)
    if existing_count is None:
        data = [(user_id, works_item_id, count)]
        len_title = "%s," * (len(list(data[0])) - 1) + "%s"
        sql.cursor.executemany(f"INSERT INTO user_work_items VALUES ({len_title})", data)
        sql.commit()
    else:
        sql.execute(
            f"UPDATE user_work_items SET count={count} WHERE user_id={user_id} AND works_item_id={works_item_id}",
            commit=True)


works_items = {
    1: {
        'name': 'Камень',
        'emoji': '🪨',
        'sell_price': 15,
        'xp': 0,

    },
    2: {
        "name": 'Медь',
        'emoji': '🌰',
        'sell_price': 35,
        'xp': 50,

    },
    3: {
        'name': 'Серебро',
        'emoji': '🪙',
        'sell_price': 55,
        'xp': 150,

    },
    4: {
        'name': 'Золото',
        'emoji': '🌼',
        'sell_price': 100,
        'xp': 500,

    },
    5: {
        'name': 'Хрусталь',
        'emoji': '🧊',
        'sell_price': 250,
        'xp': 1000,

    },
    6: {
        'name': 'Плазма',
        'emoji': '🌫',
        'sell_price': 1000,
        'xp': 5000,

    },
    7: {
        "name": "Шестерёнка",
        'emoji': '⚙️',
        'sell_price': 15,
        'xp': 0,

    },
    8: {
        'name': 'Болтик',
        'emoji': '🔩',
        'sell_price': 35,
        'xp': 150,

    },
    9: {
        'name': 'Гаечка',
        'emoji': '🔧',
        'sell_price': 100,
        'xp': 500,

    },
    10: {
        'name': 'Гвоздь',
        'emoji': '🔨',
        'sell_price': 250,
        'xp': 1000,

    },
    11: {
        'name': 'Отвёртка',
        'emoji': '🪛',
        'sell_price': 1000,
        'xp': 5000,

    }
}
