import decimal
import time

import config
from utils.main.cash import to_str
from utils.main.db import sql, timetomin
from utils.main.users import User


class Ferma:
    def __init__(self, name: str, price: int, doxod: float, nalog: int, limit: int, limit_video: int):
        self.name = name
        self.price = price
        self.doxod = doxod
        self.nalog = nalog
        self.limit = limit
        self.videoprice = price // 2
        self.limit_video = limit_video


bitcoins = {
    1: lambda: Ferma('Bit-cash 💻', 150000, 0.1, 17500, 210000, 1000),
    2: lambda: Ferma('Crypto-farm 🧑🏿‍💻', 2500000, 0.3, 150000, 1800000, 1000),
    3: lambda: Ferma('Delta-farm 🖥️', 15000000, 0.6, 5000000, 60000000, 1000),
    4: lambda: Ferma('River-bitcoin 📼', 1000000000, 1, 10000000, 120000000, 1000)
}

to_usd = lambda summ: int(float(summ) * config.bitcoin_price())


class Bitcoin:
    @staticmethod
    def create(owner: int, zindex: int):
        res = (owner, zindex, 0, time.time(), 0, 0, 1000)
        sql.insert_data([res], 'bitcoin')
        return res

    def __init__(self, owner: int = None):
        self.source = sql.select_data(owner, 'owner', True, 'bitcoin')

        self.owner: int = self.source[0]
        self.zindex: int = self.source[1]
        self.balance_: int = round(self.source[2])
        self.last: int = self.source[3]
        self.videocards: int = self.source[4]
        self.nalog: int = self.source[5]
        self.bitcoin: Ferma = bitcoins[self.zindex]()
        self.bitcoin.doxod *= self.videocards
        self.limit_video: int = self.source[6] + int(User(id=owner).donate_videocards)
        self.name = self.bitcoin.name

    def edit(self, name, value, attr=True):
        if attr:
            setattr(self, name, value)
        sql.edit_data('owner', self.owner, name, value, 'bitcoin')
        return value

    def editmany(self, attr=True, **kwargs):
        items = kwargs.items()
        query = 'UPDATE bitcoin SET '
        items_len = len(items)
        for index, item in enumerate(items):
            if attr:
                setattr(self, item[0], item[1])
            query += f'{item[0]} = {sql.item_to_sql(item[1])}'
            query += ', ' if index < items_len - 1 else ' '
        query += 'WHERE owner = {}'.format(self.owner)
        sql.execute(query=query, commit=True)

    def sell(self):
        sql.delete_data(self.owner, 'owner', 'bitcoin')
        doxod = to_usd(self.balance_) + self.bitcoin.price // 2.1
        doxod += self.bitcoin.videoprice * self.videocards
        doxod = decimal.Decimal(doxod)
        doxod -= self.nalog
        if doxod < 0:
            doxod = 0
        return doxod

    def text(self, id):
        user = User(id=id)
        donate = 0
        if user.donate:
            item = config.donates[user.donate.id]
            donate = item['videocards']
        return f'🖥️ Ваша биткоин ферма:\n' \
               f'➖➖➖➖➖➖➖➖➖➖➖\n' \
               f'🧀 Баланс биткоинов: <b>{int(self.balance)}</b> (~{to_str(to_usd(int(self.balance_)))} USD)\n' \
               f'➖➖➖➖➖➖➖➖➖➖➖\n' \
               f'🖥️ Название: <b>{self.bitcoin.name}</b>\n' \
               f'📼 Кол-во видеокарт: <b>{self.videocards} / {self.limit_video + donate}</b>\n' \
               f'💸 Доход: <b>{round(self.bitcoin.doxod, 1)}</b>BTC/час (~{to_str(to_usd(self.bitcoin.doxod))} USD)\n' \
               f'⌛ След. через: <code>{timetomin(int(decimal.Decimal(time.time()) - self.last))}</code>\n' \
               f'🌫️ Вы вложили: {to_str(int(self.videocards * (self.bitcoin.price // 4)))}\n' \
               f'💲 Налог: <code>{to_str(self.nalog)} / {to_str(self.bitcoin.limit)}</code>'

    @property
    def balance(self):
        return self.balance_

    @balance.setter
    def balance(self, value):
        self.balance_ = value
