import decimal
import time

from utils.main.cash import to_str
from utils.main.db import sql, timetomin

computers = {
    1: {
        'name': 'ASUS VivoBook S15',
        'price': 750310,
        'sell_price': 562730,
        'doxod': 56270
    },
    2: {
        'name': 'Apple MacBook Air',
        'price': 1311900,
        'sell_price': 983900,
        'doxod': 98300
    },
    3: {
        'name': 'Microsoft Surface Laptop 4 ',
        'price': 2290400,
        'sell_price': 1717800,
        'doxod': 171780
    },
    4: {
        'name': 'Razer Blade Stealth 13',
        'price': 4003450,
        'sell_price': 3002590,
        'doxod': 300250,
    },
    5: {
        'name': 'Alienware m15 R4',
        'price': 7006030,
        'sell_price': 5254520,
        'doxod': 525450
    },
    6: {
        'name': 'MSI GE76 Raider',
        'price': 21426820,
        'sell_price': 16070110,
        'doxod': 1607010
    }
}

all_computers_ = [i[1] for i in sql.get_all_data('computers')]


async def all_computers():
    return all_computers_


class Computer:
    def __init__(self, user_id: int):
        self.source: tuple = sql.select_data(user_id, 'owner', True, 'computers')
        if self.source is None:
            raise Exception('Not have computer')
        self.owner: int = self.source[0]
        self.index: int = self.source[1]
        self.computer = computers[self.index]
        self.name: str = self.source[2] if self.source[2] else self.computer['name']
        self.cash: int = self.source[3]
        self.last: int = self.source[4]
        self.strength: int = self.source[5]
        self.progress: int = self.source[6]

    @property
    def text(self):
        xd = f' ({timetomin(int(decimal.Decimal(time.time()) - self.last))})' if self.last is not None else ''
        return '{name}, Ваш компьютер:\n\n' \
               f'💻 Модель: <b>{self.name}</b>\n' \
               f'💱 Баланс: {to_str(self.cash)}\n' \
               f'💱 Доход: {to_str(self.computer["doxod"])}/час{xd}\n\n' \
               f'{"🔋" if self.strength >= 50 else "🪫"} Прочность: {self.strength}%\n' \
               f'➖➖➖➖➖➖➖➖➖➖➖\n' \
               '🧑‍💻 Прогресс взлома:\n {progres}\n\n{time}'

    def edit(self, name, value, attr=True):
        if attr:
            setattr(self, name, value)
        sql.edit_data('owner', self.owner, name, value, 'computers')
        return value

    def editmany(self, attr=True, **kwargs):
        items = kwargs.items()
        query = 'UPDATE computers SET '
        items_len = len(items)
        for index, item in enumerate(items):
            if attr:
                setattr(self, item[0], item[1])
            query += f'{item[0]} = {sql.item_to_sql(item[1])}'
            query += ', ' if index < items_len - 1 else ' '
        query += 'WHERE owner = {}'.format(self.owner)
        sql.execute(query=query, commit=True)

    @staticmethod
    def create(user_id, computer_index):
        global all_computers_
        res = (user_id, computer_index, None, 0, None, 100, 0)
        sql.insert_data([res], 'computers')
        all_computers_.append(res[0])
        return True

    def sell(self):
        sql.delete_data(self.owner, 'owner', 'computers')
        doxod = self.cash + self.computer['sell_price']
        if doxod < 0:
            doxod = 0
        return doxod
