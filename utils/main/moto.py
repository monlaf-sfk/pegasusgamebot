import decimal
import random
import time
from datetime import datetime

from utils.main.cash import to_str
from utils.main.db import sql, timetomin

motos = {
    1: {
        'name': 'Скутер 🛵',
        'price': 35000,
        'sell_price': 15000,
        'nalog': 2500,
        'limit': 30000,
        'fuel': 500
    },
    2: {
        'name': 'YZF-R1 🏍️',
        'price': 135000,
        'sell_price': 60000,
        'nalog': 5000,
        'limit': 60000,
        'fuel': 600
    },
    3: {
        'name': 'Kawasaki 🏍️',
        'price': 535000,
        'sell_price': 250000,
        'nalog': 25000,
        'limit': 300000,
        'fuel': 700
    },
    4: {
        'name': 'Suzuki 🏍️',
        'price': 2535000,
        'sell_price': 700000,
        'nalog': 55000,
        'limit': 660000,
        'fuel': 800
    },
    5: {
        'name': 'Honda 🏍️',
        'price': 21535000,
        'sell_price': 10000000,
        'nalog': 150000,
        'limit': 1800000,
        'fuel': 900
    },
    6: {
        'name': 'Ява 🏍️',
        'price': 150000000,
        'sell_price': 70000000,
        'nalog': 2150000,
        'limit': 25800000,
        'fuel': 1000
    }
}
all_moto_ = [i[1] for i in sql.get_all_data('moto')]


def all_moto():
    return all_moto_


class Moto:
    def __init__(self, user_id: int):
        self.source: tuple = sql.select_data(user_id, 'owner', True, 'moto')
        if self.source is None:
            raise Exception('Not have car')
        self.owner: int = self.source[0]
        self.index: int = self.source[1]
        self.moto = motos[self.index]
        self.name: str = self.moto["name"]
        self.number: str = self.source[2]
        self.cash: int = self.source[3]
        self.last: int = self.source[4]
        self.nalog: int = self.source[5]
        self.fuel: int = self.source[6]
        self.energy: int = self.source[7]
        self.time_buy: datetime = datetime.strptime(self.source[8], '%d-%m-%Y %H:%M:%S')
        self.stock_nalog: int = self.source[9]

    @property
    def text(self):
        lol = datetime.now() - self.time_buy
        xd2 = f'{lol.days} дн.' if lol.days > 0 else f'{int(lol.total_seconds() // 3600)} час.' \
            if lol.total_seconds() > 59 else f'{int(lol.seconds)} сек.'
        xd = f' ({timetomin(int(decimal.Decimal(float(time.time())) - self.last))})' if self.last is not None else ''
        return f'Ваша машина: (<b>{self.name}</b>)\n\n' \
               f'💲 Баланс: {to_str(self.cash)}\n' \
               f'⛽ Состояние: {self.fuel}%\n' \
               f'⚡ Энергия: {self.energy}{xd}\n' \
               f'📠 Налог: {to_str(self.nalog)} / {to_str(self.moto["limit"])}\n' \
               f'➖➖➖➖➖➖➖➖➖\n' \
               f'📅 Дата покупки: {self.time_buy} (<code>{xd2}</code>)\n'

    def edit(self, name, value, attr=True):
        if attr:
            setattr(self, name, value)
        sql.edit_data('owner', self.owner, name, value, 'moto')
        return value

    def editmany(self, attr=True, **kwargs):
        items = kwargs.items()
        query = 'UPDATE moto SET '
        items_len = len(items)
        for index, item in enumerate(items):
            if attr:
                setattr(self, item[0], item[1])
            query += f'{item[0]} = {sql.item_to_sql(item[1])}'
            query += ', ' if index < items_len - 1 else ' '
        query += 'WHERE owner = {}'.format(self.owner)
        sql.execute(query=query, commit=True)

    @staticmethod
    def create(user_id, moto_index):
        global all_moto_
        res = (user_id, moto_index, None, 0, None, 0, motos[moto_index]["fuel"], 10,
               datetime.now().strftime('%d-%m-%Y %H:%M:%S'), motos[moto_index]["nalog"])
        sql.insert_data([res], 'moto')
        all_moto_.append(res[0])
        return True

    def sell(self):
        sql.delete_data(self.owner, 'owner', 'moto')
        doxod = self.cash + self.moto['sell_price']
        doxod -= self.nalog
        if doxod < 0:
            doxod = 0
        return doxod

    def ride(self):
        km = random.randint(2, 10)
        doxod = self.moto['fuel'] * km
        self.editmany(energy=self.energy - 1, cash=self.cash + doxod, fuel=self.fuel - 1,
                      last=time.time())
        return [km, doxod]
