import decimal
import time

from utils.main.cash import to_str
from utils.main.db import sql, timetomin

businesses = {
    1: {
        'name': 'Международный банк 💶',
        'price': 2000000,
        'sell_price': 950000,
        'doxod': 75000,
        'nalog': 37500,
        'limit': 450000
    },
    2: {
        'name': 'Ателье 🧥',
        'price': 3500000,
        'sell_price': 1750000,
        'doxod': 100000,
        'nalog': 50000,
        'limit': 600000
    },
    3: {
        'name': 'Интернет-агенство 🌐',
        'price': 5500000,
        'sell_price': 2750000,
        'doxod': 250000,
        'nalog': 125000,
        'limit': 1500000
    },
    4: {
        'name': 'Сеть ресторанов 🍟',
        'price': 15000000,
        'sell_price': 7250000,
        'doxod': 500000,
        'nalog': 235000,
        'limit': 2820000,
    },
    5: {
        'name': 'Порностудия 🛌',
        'price': 50000000,
        'sell_price': 20000000,
        'doxod': 1000000,
        'nalog': 500000,
        'limit': 6000000
    },
    6: {
        'name': 'Ялан 🏬',
        'price': 100000000,
        'sell_price': 45000000,
        'doxod': 5000000,
        'nalog': 2500000,
        'limit': 30000000
    }
}


def all_businesses():
    all_businesses_ = [i[1] for i in sql.get_all_data('businesses')]
    return all_businesses_


class Business:
    def __init__(self, user_id: int):
        self.source: tuple = sql.select_data(user_id, 'owner', True, 'businesses')
        if self.source is None:
            raise Exception('Not have business')
        self.index: int = self.source[0]
        self.business = businesses[self.index]
        self.name: str = self.source[1] if self.source[1] else self.business['name']
        self.cash: int = self.source[2]
        self.last: int = self.source[3]
        self.nalog: int = self.source[4]
        self.arenda = bool(self.source[5])
        self.owner: int = self.source[6]

    @property
    def text(self):
        xd = f' ({timetomin(int(decimal.Decimal(time.time()) - self.last))})' if self.last is not None else ''
        return f'🧑‍💼 Ваш бизнес: <b>{self.name}</b>\n' \
               f'💸 Прибыль: {to_str(self.business["doxod"])}/час{xd}\n' \
               f'💰 Счёт: {to_str(self.cash)}\n' \
               f'🔒 Открыто: {"Да ✅" if self.arenda else "Нет ❌"}\n' \
               f'📠 Налог: {to_str(self.nalog)} / {to_str(self.business["limit"])}'

    def edit(self, name, value, attr=True):
        if attr:
            setattr(self, name, value)
        sql.edit_data('owner', self.owner, name, value, 'businesses')
        return value

    def editmany(self, attr=True, **kwargs):
        items = kwargs.items()
        query = 'UPDATE businesses SET '
        items_len = len(items)
        for index, item in enumerate(items):
            if attr:
                setattr(self, item[0], item[1])
            query += f'{item[0]} = {sql.item_to_sql(item[1])}'
            query += ', ' if index < items_len - 1 else ' '
        query += 'WHERE owner = {}'.format(self.owner)
        sql.execute(query=query, commit=True)

    @staticmethod
    def create(user_id, business_index):
        res = (business_index, None, 0, None, 0, False, user_id)
        sql.insert_data([res], 'businesses')
        return True

    def sell(self):
        sql.delete_data(self.owner, 'owner', 'businesses')
        doxod = self.cash + self.business['sell_price']
        doxod -= self.nalog
        if doxod < 0:
            doxod = 0
        return doxod
