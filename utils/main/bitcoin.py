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
    1: lambda: Ferma('Bit-cash 💻', 150_000, 0.5, 17_500, 210_000, 1000),
    2: lambda: Ferma('Crypto-farm 🧑🏿‍💻', 2_500_000, 1, 150_000, 1_800_000, 1000),
    3: lambda: Ferma('Delta-farm 🖥️', 15_000_000, 3, 2_500_000, 30_000_000, 1000),
    4: lambda: Ferma('River-bitcoin 📼', 100_000_000, 6, 5_000_000, 60_000_000, 1000)
}

to_usd = lambda summ: int(float(summ) * config.bitcoin_price())
all_ferma_ = [i[1] for i in sql.get_all_data('bitcoin')]


def all_ferma():
    return all_ferma_


class Bitcoin:
    @staticmethod
    def create(owner: int, zindex: int):
        global all_ferma_
        res = (owner, zindex, 0, time.time(), 0, 0, 1000, bitcoins[zindex]().doxod, bitcoins[zindex]().nalog)
        sql.insert_data([res], 'bitcoin')
        all_ferma_.append(res[0])
        return res

    def __init__(self, owner: int = None):
        self.source = sql.select_data(owner, 'owner', True, 'bitcoin')
        if self.source is None:
            raise Exception('Not have bitcoin')
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
        self.stock_doxod: int = self.source[7]
        self.stock_nalog: int = self.source[8]

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
