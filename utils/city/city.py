from datetime import datetime

from psycopg2._json import Json

from utils.city.buildings import water_build, house_build, energy_build
from utils.main.db import sql


class City:
    def __init__(self, user_id: int):
        self.source: tuple = sql.select_data(user_id, 'owner', True, 'city')
        if self.source is None:
            raise Exception('Not have city')

        self.owner: str = self.source[0]
        self.name: int = self.source[1]
        self.kazna: int = self.source[2]
        self.citizens: int = self.source[3]
        self.happynes: float = self.source[4]
        self.workers: int = self.source[5]
        self.taxes: int = self.source[6]
        self.water: dict = self.source[7]
        self.energy: dict = self.source[8]
        self.road: int = self.source[9]
        self.house: dict = self.source[10]
        self.last_online: datetime = self.source[10]

    def editmany(self, attr=True, **kwargs):
        items = kwargs.items()
        query = 'UPDATE city SET '
        items_len = len(items)
        for index, item in enumerate(items):
            if attr:
                setattr(self, item[0], item[1])
            query += f'{item[0]} = {sql.item_to_sql(item[1])}'
            query += ', ' if index < items_len - 1 else ' '
        query += 'WHERE owner = {}'.format(self.owner)
        sql.execute(query=query, commit=True)

    def get_count_build(self):
        count = 0
        for index, builds in enumerate(self.water, start=1):
            count += self.water[f"{index}"]["count_build"]
        for index, builds in enumerate(self.energy, start=1):
            count += self.energy[f"{index}"]["count_build"]
        for index, builds in enumerate(self.house, start=1):
            count += self.house[f"{index}"]["count_build"]

        return count

    @staticmethod
    def create(user_id, name):
        res = (user_id, name, 0, 0, 100.0, 0, 2, Json(water_build), Json(energy_build), 20, Json(house_build),
               datetime.now().strftime('%d-%m-%Y %H:%M:%S'))
        sql.insert_data([res], 'city')
        return True

    def edit(self, name, value, attr=True):
        if attr:
            setattr(self, name, value)
        sql.edit_data('owner', self.owner, name, value, 'city')
        return value

    def sell(self):
        sql.delete_data(self.owner, 'owner', 'city')
