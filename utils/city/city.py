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
        self.water: iter | list = ([int(x.split(':')[0]), int(x.split(':')[1])] for x in self.source[7].split(',') if
                                   x and ':' in x)
        self.energy: iter | list = ([int(x.split(':')[0]), int(x.split(':')[1])] for x in self.source[8].split(',') if
                                    x and ':' in x)
        self.road: int = self.source[9]
        self.house: iter | list = ([int(x.split(':')[0]), int(x.split(':')[1])] for x in self.source[10].split(',') if
                                   x and ':' in x)

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

    def get_water(self, item_index: int = None, item_id: int = None):
        if item_id is not None:
            item = None
            for ind, i in enumerate(self.water):
                if item_id == i[0]:
                    item = i
                    break
            if item:
                return item
        else:
            return self.water[item_index]

    def set_water(self, item_index: int = None, item_id: int = None, x: int = 1):
        if item_id is not None:
            item = None
            for ind, i in enumerate(self.water):
                if item_id == i[0]:
                    item = i
                    break
            if item is None:
                self.water.append([item_id, 0])
                item = [item_id, 0]
                ind = len(self.water) - 1
            self.water[ind] = [item_id, item[1] + x]
            if (item[1] + x) <= 0:
                self.water.remove(self.water[ind])

            self.edit('water', ','.join(f'{x[0]}:{x[1]}' for x in self.water), False)
        else:
            a = self.water[item_index]
            if (a[1] + x) <= 0:
                self.water.remove(a)
            else:
                self.water[item_index] = [a[0], a[1] + x]
            self.edit('water', ','.join(f'{x[0]}:{x[1]}' for x in self.water), False)

    def get_energy(self, item_index: int = None, item_id: int = None):
        if item_id is not None:
            item = None
            for ind, i in enumerate(self.energy):
                if item_id == i[0]:
                    item = i
                    break
            if item:
                return item
        else:
            return self.energy[item_index]

    def set_energy(self, item_index: int = None, item_id: int = None, x: int = 1):

        if item_id is not None:
            item = None
            for ind, i in enumerate(self.energy):
                if item_id == i[0]:
                    item = i
                    break
            if item is None:
                self.energy.append([item_id, 0])
                item = [item_id, 0]
                ind = len(self.energy) - 1
            self.energy[ind] = [item_id, item[1] + x]
            if (item[1] + x) <= 0:
                self.energy.remove(self.energy[ind])

            self.edit('energy', ','.join(f'{x[0]}:{x[1]}' for x in self.energy), False)
        else:
            a = self.energy[item_index]
            if (a[1] + x) <= 0:
                self.energy.remove(a)
            else:
                self.energy[item_index] = [a[0], a[1] + x]
            self.edit('energy', ','.join(f'{x[0]}:{x[1]}' for x in self.energy), False)

    def get_house(self, item_index: int = None, item_id: int = None):
        if item_id is not None:
            item = None
            for ind, i in enumerate(self.house):
                if item_id == i[0]:
                    item = i
                    break
            if item:
                return item
        else:
            return self.house[item_index]

    def set_house(self, item_index: int = None, item_id: int = None, x: int = 1):

        if item_id is not None:
            item = None
            for ind, i in enumerate(self.house):
                if item_id == i[0]:
                    item = i
                    break
            if item is None:
                self.house.append([item_id, 0])
                item = [item_id, 0]
                ind = len(self.house) - 1
            self.house[ind] = [item_id, item[1] + x]
            if (item[1] + x) <= 0:
                self.house.remove(self.house[ind])

            self.edit('house', ','.join(f'{x[0]}:{x[1]}' for x in self.house), False)
        else:
            a = self.house[item_index]
            if (a[1] + x) <= 0:
                self.house.remove(a)
            else:
                self.house[item_index] = [a[0], a[1] + x]
            self.edit('house', ','.join(f'{x[0]}:{x[1]}' for x in self.house), False)

    def get_count_build(self):
        count = 0
        for index, item in enumerate(self.water, start=1):
            count += item[1]
        for index, item in enumerate(self.energy, start=1):
            count += item[1]
        for index, item in enumerate(self.house, start=1):
            count += item[1]
        return count

    @staticmethod
    def create(user_id, name):
        res = (user_id, name, 0, 0, 100.0, 0, 2, '', '', 20, '')
        sql.insert_data([res], 'city')
        return True

    def edit(self, name, value, attr=True):
        if attr:
            setattr(self, name, value)
        sql.edit_data('owner', self.owner, name, value, 'city')
        return value

    def sell(self):
        sql.delete_data(self.owner, 'owner', 'city')
