import json

from config import armory_img
from utils.main.db import sql
from utils.weapons.weapon import weapons_item


class Armory:
    def __init__(self, uniq_id: int = None, armed: bool = None, user_id: int = None):
        if armed and user_id:
            self.source: tuple = sql.execute(
                f"SELECT * FROM armory WHERE user_id ={user_id} AND armed= True",
                fetchone=True)
        else:
            self.source: tuple = sql.select_data(uniq_id, 'uniq_id', True, 'armory')
        if self.source is None:
            raise Exception('Not have armory')
        self.uniq_id: int = self.source[0]
        self.user_id: int = self.source[1]
        self.weapon_id: int = self.source[2]
        self.type: str = self.source[3]
        self.durability: int = self.source[4]
        self.armed: bool = self.source[5]
        self.weapon: dict = weapons_item[self.type][self.weapon_id]
        self.image: str = armory_img[self.type]

    def edit(self, name, value, attr=True):
        if attr:
            setattr(self, name, value)
        sql.edit_data('uniq_id', self.uniq_id, name, value, 'armory')
        return value

    def editmany(self, attr=True, **kwargs):
        items = kwargs.items()
        query = 'UPDATE armory SET '
        items_len = len(items)
        for index, item in enumerate(items):
            if attr:
                setattr(self, item[0], item[1])
            query += f'{item[0]} = {sql.item_to_sql(item[1])}'
            query += ', ' if index < items_len - 1 else ' '
        query += 'WHERE uniq_id = {}'.format(self.uniq_id)
        sql.execute(query=query, commit=True)

    @staticmethod
    def create_armory(user_id: int, id_weapons: int, type: str):
        sql.get_cursor().execute("INSERT INTO armory VALUES(DEFAULT,%s,%s,%s,%s,%s)",
                                 (
                                     user_id, id_weapons, type, weapons_item[type][id_weapons]['max_durability'],
                                     False))
        return True

    @staticmethod
    def delete(uniq_id):

        sql.delete_data(uniq_id, 'uniq_id', 'armory')
        return True

    def parsing(self):
        sql.delete_data(self.uniq_id, 'uniq_id', 'armory')
        disassemble = self.weapon['disassemble']
        return disassemble


class ArmoryInv:
    def __init__(self, user_id: int):
        self.source: tuple = sql.select_data(user_id, 'user_id', True, 'armory_inv')
        if self.source is None:
            self.source = ArmoryInv.create_armory_inv(user_id)
        self.user_id: int = self.source[0]
        self.min_damage: int = int(self.source[1])
        self.max_damage: int = int(self.source[2])
        self.tokens: int = int(self.source[3])
        self.repair_kit: int = int(self.source[4])
        self.fragments: int = int(self.source[5])

    def edit(self, name, value, attr=True):
        if attr:
            setattr(self, name, value)
        sql.edit_data('user_id', self.user_id, name, value, 'armory_inv')
        return value

    def editmany(self, attr=True, **kwargs):
        items = kwargs.items()
        query = 'UPDATE armory_inv SET '
        items_len = len(items)
        for index, item in enumerate(items):
            if attr:
                setattr(self, item[0], item[1])
            query += f'{item[0]} = {sql.item_to_sql(item[1])}'
            query += ', ' if index < items_len - 1 else ' '
        query += 'WHERE user_id = {}'.format(self.user_id)
        sql.execute(query=query, commit=True)

    @staticmethod
    def create_armory_inv(user_id: int):
        res = (user_id, 500, 1000, 0, 0, 0)
        sql.insert_data([res], "armory_inv")
        return res
