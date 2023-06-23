import decimal
import random
import time
from datetime import datetime

from utils.main.cash import to_str
from utils.main.db import sql, timetomin

cars = {
    1: {
        'name': 'Жигули 🚗',
        'price': 50000,
        'sell_price': 20000,
        'nalog': 2500,
        'limit': 36000,
        'fuel': 200
    },
    2: {
        'name': 'Audi 🚗',
        'price': 250000,
        'sell_price': 115000,
        'nalog': 10000,
        'limit': 120000,
        'fuel': 400
    },
    3: {
        'name': 'BMW 🚗',
        'price': 1000000,
        'sell_price': 450000,
        'nalog': 50000,
        'limit': 600000,
        'fuel': 500
    },
    4: {
        'name': 'Bentley 🚗',
        'price': 5000000,
        'sell_price': 2250000,
        'nalog': 70000,
        'limit': 840000,
        'fuel': 600
    },
    5: {
        'name': 'Formula 1 🏎️',
        'price': 25000000,
        'sell_price': 12000000,
        'nalog': 250000,
        'limit': 3000000,
        'fuel': 700
    },
    6: {
        'name': 'Tesla Roadster 🛰️',
        'price': 50000000,
        'sell_price': 23500000,
        'nalog': 1000000,
        'limit': 12000000,
        'fuel': 800
    }
}

all_cars_ = [i[1] for i in sql.get_all_data('cars')]


def all_cars():
    return all_cars_


class Car:
    def __init__(self, user_id: int):
        self.source: tuple = sql.select_data(user_id, 'owner', True, 'cars')
        if self.source is None:
            raise Exception('Not have car')

        self.index: int = self.source[0]
        self.car = cars[self.index]
        self.name: str = self.car["name"]
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
        return f'Ваша машина: (<b>{self.name}</b>)\n\n' \
               f'💲 Баланс: {to_str(self.cash)}\n' \
               f'⛽ Состояние: {self.fuel}%\n' \
               f'⚡ Энергия: {self.energy}{xd}\n' \
               f'📠 Налог: {to_str(self.nalog)} / {to_str(self.car["limit"])}\n' \
               f'➖➖➖➖➖➖➖➖➖\n' \
               f'📅 Дата покупки: {self.time_buy} (<code>{xd2}</code>)\n'

    def edit(self, name, value, attr=True):
        if attr:
            setattr(self, name, value)
        sql.edit_data('owner', self.owner, name, value, 'cars')
        return value

    def editmany(self, attr=True, **kwargs):
        items = kwargs.items()
        query = 'UPDATE cars SET '
        items_len = len(items)
        for index, item in enumerate(items):
            if attr:
                setattr(self, item[0], item[1])
            query += f'{item[0]} = {sql.item_to_sql(item[1])}'
            query += ', ' if index < items_len - 1 else ' '
        query += 'WHERE owner = {}'.format(self.owner)
        sql.execute(query=query, commit=True)

    @staticmethod
    def create(user_id, car_index):
        global all_cars_
        res = (
            car_index, None, 0, None, 0, cars[car_index]["fuel"], 10, user_id,
            datetime.now().strftime('%d-%m-%Y %H:%M:%S'))
        sql.insert_data([res], 'cars')
        all_cars_.append(res[0])
        return True

    def sell(self):
        sql.delete_data(self.owner, 'owner', 'cars')
        doxod = self.cash + self.car['sell_price']
        doxod -= self.nalog
        if doxod < 0:
            doxod = 0
        return doxod

    def ride(self):
        km = random.randint(2, 10)
        doxod = self.car['fuel'] * km
        self.editmany(energy=self.energy - 1, cash=self.cash + doxod, fuel=self.fuel - 1,
                      last=time.time())
        return [km, doxod]
