from utils.main.db import sql


def get_item_count(case_id, user_id):
    count = sql.execute(f"SELECT count FROM user_cases WHERE user_id={user_id} AND case_id={case_id}",
                        fetchone=True)
    return count['count'] if count else None


def fetch_all_case_counts(user_id):
    case_counts = sql.execute(f"SELECT case_id, count FROM user_cases WHERE user_id={user_id}", fetch=True)

    if case_counts is None:
        return {}  # Return an empty dictionary if no records are found
    return {case['case_id']: case['count'] for case in case_counts}


def set_item_count(case_id, user_id, count):
    existing_count = get_item_count(case_id, user_id)
    if existing_count is None:
        data = [(user_id, case_id, count)]
        len_title = "%s," * (len(list(data[0])) - 1) + "%s"
        sql.cursor.executemany(f"INSERT INTO user_cases VALUES ({len_title})", data)
        sql.commit()
    else:
        sql.execute(f"UPDATE user_cases SET count={count} WHERE user_id={user_id} AND case_id={case_id}",
                    commit=True)


item_case = {
    1: {
        "name": "Обычный кейс",
        "emoji": "🥡",
        "price": 10_000_000,

    },
    2: {
        "name": "Средний кейс",
        "emoji": "🎁",
        "price": 30_000_000,

    },
    3: {
        "name": "Ультра кейс",
        "price": 50_000_000,
        "emoji": "☄️",

    },
    4: {
        "name": "Тайный кейс",
        "price": False,
        "emoji": "㊙️",

    },
    5: {
        "name": "Выигрышный кейс",
        "price": False,
        "emoji": "🥇",

    },
    6: {
        "name": "Утешительный кейс",
        "price": False,
        "emoji": "🥈",

    }
}
