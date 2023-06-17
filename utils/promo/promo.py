from __future__ import annotations
from utils.main.db import sql


def all_promo():
    all_promo_ = [str(i[1]).lower() for i in sql.get_all_data('promocodes')]
    return all_promo_


class Promocode:
    def __init__(self, name: str):
        self.source = sql.execute(f"SELECT * FROM promocodes WHERE LOWER(name) ='{name}'", False, True)
        if len(self.source) == 0:
            raise Exception('Промокод не найден!')
        self.source = self.source[-1]
        self.owner_id: int = self.source[0]
        self.name: str = str(self.source[1])
        self.activations: int = self.source[2]
        self.users: list = [int(x) for x in self.source[3].split(',') if x]
        self.status: bool = bool(self.source[4])
        self.summ: int = self.source[5]
        self.xd: int = self.source[6]

    def add_user(self, user_id: int):
        self.users.append(user_id)

        sql.edit_data('name', self.name, 'users', ','.join(str(x) for x in self.users), 'promocodes')

    def finish(self):
        sql.edit_data('name', self.name, 'status', False, 'promocodes')

    @staticmethod
    def create(name: str, activations: int, summ: int, xd: int, id: int):
        res = (id, name.lower(), activations, '', True, summ, xd)
        sql.insert_data([res], 'promocodes')
