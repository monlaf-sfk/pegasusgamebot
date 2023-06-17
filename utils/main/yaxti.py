import decimal
import random
import time
from datetime import datetime

from utils.main.cash import to_str
from utils.main.db import sql, timetomin

yaxti = {
    1: {
        'name': 'Небздящий ⛵',
        'price': 150000,
        'sell_price': 20000,
        'nalog': 500,
        'limit': 6000,
        'fuel': 400
    },
    2: {
        'name': 'Пес датый ⛵',
        'price': 1000000,
        'sell_price': 450000,
        'nalog': 10000,
        'limit': 120000,
        'fuel': 500
    },
    3: {
        'name': 'Батька ⛵',
        'price': 3500000,
        'sell_price': 1700000,
        'nalog': 15000,
        'limit': 180000,
        'fuel': 600
    },
    4: {
        'name': 'Непотопляемый 🚢',
        'price': 15000000,
        'sell_price': 7000000,
        'nalog': 150000,
        'limit': 1800000,
        'fuel': 800
    }
}


def all_yaxti():
    all_yaxti_ = [i[1] for i in sql.get_all_data('yaxti')]
    return all_yaxti_


class Yaxta:
    def __init__(self, user_id: int):
        self.source: tuple = sql.select_data(user_id, 'owner', True, 'yaxti')
        if self.source is None:
            raise Exception('Not have yaxta')
        self.index: int = self.source[0]
        self.yaxta = yaxti[self.index]
        self.name: str = self.yaxta["name"]
        self.number: str = self.source[1]
        self.cash: int = self.source[2]
        self.last: int = self.source[3]
        self.nalog: int = self.source[4]
        self.fuel: int = self.source[5]
        self.energy: int = self.source[6]
        self.owner: int = self.source[7]
        self.time_buy: datetime = datetime.strptime(self.source[8], '%d-%m-%Y %H:%M:%S')

    @property
    def text(self):
        lol = datetime.now() - self.time_buy
        xd2 = f'{lol.days} дн.' if lol.days > 0 else f'{int(lol.total_seconds() // 3600)} час.' \
            if lol.total_seconds() > 59 else f'{int(lol.seconds)} сек.'
        xd = f' ({timetomin(int(decimal.Decimal(time.time()) - self.last))})' if self.last is not None else ''
        return f'Ваша яхта: (<b>{self.name}</b>)\n\n' \
               f'💲 Баланс: {to_str(self.cash)}\n' \
               f'⛽ Состояние: {self.fuel}%\n' \
               f'⚡ Энергия: {self.energy}{xd}\n' \
               f'📠 Налог: {to_str(self.nalog)} / {to_str(self.yaxta["limit"])}\n' \
               f'➖➖➖➖➖➖➖➖➖\n' \
               f'📅 Дата покупки: {self.time_buy} (<code>{xd2}</code>)\n'

    def edit(self, name, value, attr=True):
        if attr:
            setattr(self, name, value)
        sql.edit_data('owner', self.owner, name, value, 'yaxti')
        return value

    def editmany(self, attr=True, **kwargs):
        items = kwargs.items()
        query = 'UPDATE yaxti SET '
        items_len = len(items)
        for index, item in enumerate(items):
            if attr:
                setattr(self, item[0], item[1])
            query += f'{item[0]} = {sql.item_to_sql(item[1])}'
            query += ', ' if index < items_len - 1 else ' '
        query += 'WHERE owner = {}'.format(self.owner)
        sql.execute(query=query, commit=True)

    @staticmethod
    def create(user_id, yaxta_index):
        res = (yaxta_index, None, 0, None, 0, yaxti[yaxta_index]["fuel"], 10, user_id,
               datetime.now().strftime('%d-%m-%Y %H:%M:%S'))
        sql.insert_data([res], 'yaxti')
        return True

    def sell(self):
        sql.delete_data(self.owner, 'owner', 'yaxti')
        doxod = self.cash + self.yaxta['sell_price']
        doxod -= self.nalog
        if doxod < 0:
            doxod = 0
        return doxod

    def ride(self):
        km = random.randint(2, 10)
        doxod = self.yaxta['fuel'] * km
        self.editmany(energy=self.energy - 1, cash=self.cash + doxod, fuel=self.fuel - 1,
                      last=time.time())
        return [km, doxod]
