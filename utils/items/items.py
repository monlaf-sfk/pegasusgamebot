from utils.main.db import sql


class ItemsRob:
    def __init__(self, item_id: int):
        self.source: dict = sql.select_data(item_id, 'id', True, 'items_rob')
        if self.source is None:
            raise Exception(f"Item with id {item_id} not found")
        self.item_id: int = item_id
        self.name: str = self.source['name']
        self.emoji: str = self.source['emoji']
        self.sell_price: int = self.source['sell_price']

    @staticmethod
    def create(name, emoji, sell_price):
        res = (name, emoji, sell_price)
        item_id = sql.insert_data([res], 'items_rob')
        return ItemsRob(item_id)

    def edit(self, name, value):
        setattr(self, name, value)
        sql.edit_data('id', self.item_id, name, value, 'items_rob')
        return value

    def get_item_count(self, user_id):
        count = sql.execute(f"SELECT count FROM user_items_rob WHERE user_id={user_id} AND item_id={self.item_id}",
                            fetchone=True)
        return count['count'] if count else None

    def set_item_count(self, user_id, count):
        existing_count = self.get_item_count(user_id)
        if existing_count is None:
            data = [(user_id, self.item_id, count)]
            len_title = "%s," * (len(list(data[0])) - 1) + "%s"
            sql.cursor.executemany(f"INSERT INTO user_items_rob VALUES (DEFAULT,{len_title})", data)
            sql.commit()
        else:
            sql.execute(f"UPDATE user_items_rob SET count={count} WHERE user_id={user_id} AND item_id={self.item_id}",
                        commit=True)

    @staticmethod
    def check_item(user_id, item_id):
        item_id = sql.execute(f"SELECT item_id FROM user_items_rob WHERE user_id={user_id}"
                              f" and item_id={item_id} and count>0",
                              fetchone=True)
        if item_id and item_id[0]:
            return True
        return False

    @staticmethod
    def check_allitems(user_id, items):
        item_ids = sql.execute(f"SELECT item_id FROM user_items_rob WHERE user_id={user_id} and count>0",
                               fetch=True)
        for item_id in items:
            # Проверка, существует ли предмет в базе данных по item_id
            if item_ids and any(item_id == item_id2[0] for item_id2 in item_ids):
                continue
            else:
                return False
        return True


items_rob = {
    1: {
        "name": "Пистолет",
        "emoji": "🔫",
        "sell_price": 10000,
    },
    2: {
        "name": "Тапор",
        "emoji": "🪓",
        "sell_price": 15000,

    },
    3: {
        "name": 'Нож',
        "emoji": "🔪",
        "sell_price": 28000,

    },
    4: {
        "name": 'Динамит',
        "emoji": '🧨',
        'sell_price': 32000,

    },
    5: {
        "name": "Маска",
        "emoji": '🎭',
        'sell_price': 39000,

    },
    6: {
        "name": 'Перчатки',
        'emoji': '🧤',
        'sell_price': 47000,

    },
    7: {
        "name": 'Молоток',
        'emoji': '🔨',
        'sell_price': 51000,

    },
    8: {
        "name": "Бита",
        "emoji": '🏏',
        "sell_price": 55000,

    },
    9: {
        "name": "Мешок",
        "emoji": "🎒",
        "sell_price": 70000,

    },
    10: {
        "name": "Электрошокер",
        'emoji': '⚡',
        "sell_price": 80000,
    },
    11: {
        "name": 'Чулки',
        'emoji': '🧦',
        'sell_price': 88000,
    },
    12: {
        "name": "Сумка",
        "emoji": "👜",
        "sell_price": 92000,
    },
    13: {
        "name": 'Фонарик',
        'emoji': '🔦',
        'sell_price': 95000,
    },
    14: {
        "name": "Отвертка",
        "emoji": "🪛",
        "sell_price": 105000,
    }
}


def add_items_to_database():
    existing_items = sql.execute('SELECT id FROM items_rob', fetch=True)

    update_queries = []
    for item_id, item_data in items_rob.items():
        # Проверка, существует ли предмет в базе данных по item_id
        if existing_items and any(item_id == existing_item[0] for existing_item in existing_items):
            continue
        # Добавление предмета в базу данных
        update_queries.append((item_id, item_data['name'], item_data['emoji'], item_data['sell_price']))
    if update_queries:
        len_title = "%s," * (len(list(update_queries[0])) - 1) + "%s"
        curs = sql.conn.cursor()
        curs.executemany(f"INSERT INTO items_rob VALUES ({len_title})", update_queries)
        sql.commit()


add_items_to_database()
