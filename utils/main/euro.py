from config import euro_price, uah_price
from utils.main.cash import to_str
from utils.main.db import sql

euro_to_usd = lambda summ: int(summ * euro_price())
uah_to_usd = lambda summ: int(summ * uah_price())


class Euro:
    def __init__(self, owner: int):
        self.source: tuple = sql.select_data(owner, 'owner', True, 'euro')
        if self.source is None:
            self.source: tuple = Euro.create(owner)

        self.owner: int = self.source[0]
        self.balance: int = self.source[1]
        self.level: int = self.source[2]
        self.spaciousness: int = self.level * 1000

    @staticmethod
    def create(owner: int):
        res = (owner, 0, 0)
        sql.insert_data([res], 'euro')
        return res

    def edit(self, name, value, attr=True):
        if attr:
            setattr(self, name, value)
        sql.edit_data('owner', self.owner, name, value, 'euro')
        return value

    def editmany(self, attr=True, **kwargs):
        items = kwargs.items()
        query = 'UPDATE euro SET '
        items_len = len(items)
        for index, item in enumerate(items):
            if attr:
                setattr(self, item[0], item[1])
            query += f'{item[0]} = {sql.item_to_sql(item[1])}'
            query += ', ' if index < items_len - 1 else ' '
        query += 'WHERE owner = {}'.format(self.owner)
        sql.execute(query=query, commit=True)

    @property
    def text(self):
        return f'🥡 Ваша кладовка:\n' \
               f'💶 Баланс: {to_str(self.balance).replace("$", "€")}\n' \
               f'🥫 Вместимость: {to_str(self.spaciousness).replace("$", "€")}\n' \
               f'➖➖➖➖➖➖➖➖➖➖➖➖\n' \
               f'💶 Текущий курс: {to_str(euro_to_usd(1))}'


class Uah:
    def __init__(self, owner: int):
        self.source: tuple = sql.select_data(owner, 'owner', True, 'uah')
        if self.source is None:
            self.source: tuple = Uah.create(owner)

        self.owner: int = self.source[0]
        self.balance: int = self.source[1]
        self.level: int = self.source[2]
        self.spaciousness: int = self.level * 1000

    @staticmethod
    def create(owner: int):
        res = (owner, 0, 0)
        sql.insert_data([res], 'uah')
        return res

    def edit(self, name, value, attr=True):
        if attr:
            setattr(self, name, value)
        sql.edit_data('owner', self.owner, name, value, 'uah')
        return value

    def editmany(self, attr=True, **kwargs):
        items = kwargs.items()
        query = 'UPDATE uah SET '
        items_len = len(items)
        for index, item in enumerate(items):
            if attr:
                setattr(self, item[0], item[1])
            query += f'{item[0]} = {sql.item_to_sql(item[1])}'
            query += ', ' if index < items_len - 1 else ' '
        query += 'WHERE owner = {}'.format(self.owner)
        sql.execute(query=query, commit=True)

    @property
    def text(self):
        return f'🥡 Ваша кладовка:\n' \
               f'💷 Баланс: {to_str(self.balance).replace("$", "¥")}\n' \
               f'🥫 Вместимость: {to_str(self.spaciousness).replace("$", "¥")}\n' \
               f'➖➖➖➖➖➖➖➖➖➖➖➖\n' \
               f'💹 Текущий курс: {to_str(uah_to_usd(1))}'
