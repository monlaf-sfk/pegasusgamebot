import decimal
import random
import time
from datetime import datetime

from utils.main.cash import to_str
from utils.main.db import sql, timetomin

vertoleti = {
    1: {
        'name': 'BEll 🚁',
        'price': 12500000,
        'sell_price': 6000000,
        'nalog': 300_000,
        'limit': 3_600_000,
        'fuel': 400
    },
    2: {
        'name': 'Augusta Westland 🚁',
        'price': 50000000,
        'sell_price': 20000000,
        'nalog': 1000000,
        'limit': 12000_000,
        'fuel': 500
    },
    3: {
        'name': 'Robinson 🚁',
        'price': 150000000,
        'sell_price': 60000000,
        'nalog': 12_500_000,
        'limit': 150_000_000,
        'fuel': 600
    },
    4: {
        'name': 'McDonnell 🚁',
        'price': 12000000000,
        'sell_price': 55000000,
        'nalog': 25_000_000,
        'limit': 300_000_000,
        'fuel': 700
    },
}

all_vertoleti_ = [i[1] for i in sql.get_all_data('vertoleti')]


def all_vertoleti():
    return all_vertoleti_


class Vertolet:
    def __init__(self, user_id: int):
        self.source: tuple = sql.select_data(user_id, 'owner', True, 'vertoleti')
        if self.source is None:
            raise Exception('Not have vertolet')
        self.index: int = self.source[0]
        self.vertolet = vertoleti[self.index]
        self.name: str = self.vertolet["name"]
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
        return f'Ваш вертолёт: (<b>{self.name}</b>)\n\n' \
               f'💲 Баланс: {to_str(self.cash)}\n' \
               f'⛽ Состояние: {self.fuel}%\n' \
               f'⚡ Энергия: {self.energy}{xd}\n' \
               f'📠 Налог: {to_str(self.nalog)} / {to_str(self.vertolet["limit"])}\n' \
               f'➖➖➖➖➖➖➖➖➖\n' \
               f'📅 Дата покупки: {self.time_buy} (<code>{xd2}</code>)\n'

    def edit(self, name, value, attr=True):
        if attr:
            setattr(self, name, value)
        sql.edit_data('owner', self.owner, name, value, 'vertoleti')
        return value

    def editmany(self, attr=True, **kwargs):
        items = kwargs.items()
        query = 'UPDATE vertoleti SET '
        items_len = len(items)
        for index, item in enumerate(items):
            if attr:
                setattr(self, item[0], item[1])
            query += f'{item[0]} = {sql.item_to_sql(item[1])}'
            query += ', ' if index < items_len - 1 else ' '
        query += 'WHERE owner = {}'.format(self.owner)
        sql.execute(query=query, commit=True)

    @staticmethod
    def create(user_id, vertolet_index):
        global all_vertoleti_
        res = (vertolet_index, None, 0, None, 0, vertoleti[vertolet_index]["fuel"], 10, user_id,
               datetime.now().strftime('%d-%m-%Y %H:%M:%S'))
        sql.insert_data([res], 'vertoleti')
        all_vertoleti_.append(res[0])
        return True

    def sell(self):
        sql.delete_data(self.owner, 'owner', 'vertoleti')
        doxod = self.cash + self.vertolet['sell_price']
        doxod -= self.nalog
        if doxod < 0:
            doxod = 0
        return doxod

    def ride(self):
        km = random.randint(2, 10)
        doxod = self.vertolet['fuel'] * km
        self.editmany(energy=self.energy - 1, cash=self.cash + doxod, fuel=self.fuel - 1,
                      last=time.time())
        return [km, doxod]
