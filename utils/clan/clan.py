from datetime import datetime

from utils.main.db import sql

status_clan = {
    0: {"name": "Участник",
        },
    1: {
        "name": "Соруководитель",
    },
    2: {
        "name": "Глава",
    }
}


class Clan:
    def __init__(self, **kwargs):

        if 'clan_id' in kwargs:
            clan_id = kwargs['clan_id']
            self.source: tuple = sql.select_data(clan_id, 'id', True, 'clans')
        elif 'owner' in kwargs:
            owner = kwargs['owner']
            self.source: tuple = sql.select_data(owner, 'owner', True, 'clans')
        else:
            self.source = None
        if self.source is None:
            raise Exception('Not have clan')
        self.id: int = self.source[0]
        self.name: str = self.source[1]
        self.owner: int = self.source[2]
        self.rating: int = self.source[3]
        self.kazna: int = self.source[4]
        self.win: int = self.source[5]
        self.lose: int = self.source[6]
        self.members: int = self.source[7]
        self.type: int = self.source[8]
        self.power: int = self.source[9]
        self.prefix: str = self.source[10]
        self.level: int = self.source[11]
        self.invites: iter | list = self.source[12].split(',')
        self.reg_date: datetime = datetime.strptime(self.source[13], '%d-%m-%Y %H:%M:%S')
        self.last_attack: int = self.source[14]

    def editmany(self, attr=True, **kwargs):
        items = kwargs.items()
        query = 'UPDATE clans SET '
        items_len = len(items)
        for index, item in enumerate(items):
            if attr:
                setattr(self, item[0], item[1])
            query += f'{item[0]} = {sql.item_to_sql(item[1])}'
            query += ', ' if index < items_len - 1 else ' '
        query += 'WHERE id = {}'.format(self.id)
        sql.execute(query=query, commit=True)

    @staticmethod
    def create(user_id, name):
        all_clan = sql.get_all_data('clans') if not None else 1
        res = (len(all_clan) + 1 if len(all_clan) > 0 else 1, name, user_id, 0, 0, 0, 0, 1, 0, 0, '', 1, '',
               datetime.now().strftime('%d-%m-%Y %H:%M:%S'), None)
        sql.insert_data([res], 'clans')
        return True

    def edit(self, name, value, attr=True):
        if attr:
            setattr(self, name, value)
        sql.edit_data('id', self.id, name, value, 'clans')
        return value

    def add_invites(self, user_id):
        self.invites = list(self.invites)
        if self.invites[0] == '':
            self.edit('invites', user_id, False)
        if user_id is not None and self.invites[0] != '':
            item = None
            for i in self.invites:
                if user_id == int(i):
                    item = i
                    break
            if item is None:
                self.invites.append(str(user_id))

                self.edit('invites', ','.join(f'{x}' for x in self.invites), False)

    def dell_invites(self, user_id):
        self.invites = list(self.invites)
        if user_id is not None:
            item = None
            for i in self.invites:
                if user_id == i:
                    self.invites.remove(i)
                    item = 1
                    break
            if item:
                self.edit('invites', ','.join(f'{x}' for x in self.invites), False)


class Clanuser:
    def __init__(self, user_id: int):
        self.source: tuple = sql.select_data(user_id, 'id', True, 'clan_users')
        if self.source is None:
            raise Exception('Not have clan')
        self.id_clan: int = self.source[0]
        self.id: int = self.source[1]
        self.rating: int = self.source[2]
        self.status: int = self.source[3]
        self.items: iter | list = ([int(x.split(':')[0]), int(x.split(':')[1])] for x in self.source[4].split(',') if
                                   x and ':' in x)
        self.reg_date: datetime = datetime.strptime(self.source[5], '%d-%m-%Y %H:%M:%S')

    def editmany(self, attr=True, **kwargs):
        items = kwargs.items()
        query = 'UPDATE clan_users SET '
        items_len = len(items)
        for index, item in enumerate(items):
            if attr:
                setattr(self, item[0], item[1])
            query += f'{item[0]} = {sql.item_to_sql(item[1])}'
            query += ', ' if index < items_len - 1 else ' '
        query += 'WHERE id = {}'.format(self.id)
        sql.execute(query=query, commit=True)

    def get_item(self, item_index: int = None, item_id: int = None):
        if item_id is not None:
            item = None
            for ind, i in enumerate(self.items):
                if item_id == i[0]:
                    item = i
                    break
            if item:
                return item
        else:
            return self.items[item_index]

    def set_item(self, item_index: int = None, item_id: int = None, x: int = 1):
        if item_id is not None:
            item = None
            for ind, i in enumerate(self.items):

                if item_id == i[0]:
                    item = i
                    break
            if item is None:
                self.items.append([item_id, 0])
                item = [item_id, 0]
                ind = len(self.items) - 1

            self.items[ind] = [item_id, item[1] + x]
            if (item[1] + x) <= 0:
                self.items.remove(self.items[ind])
            self.edit('items', ','.join(f'{x[0]}:{x[1]}' for x in self.items), False)
        else:
            a = self.items[item_index]
            if (a[1] + x) <= 0:
                self.items.remove(a)
            else:
                self.items[item_index] = [a[0], a[1] + x]

            self.edit('items', ','.join(f'{x[0]}:{x[1]}' for x in self.items), False)

    @staticmethod
    def create(user_id, id_clan):
        res = (id_clan, user_id, 0, 2, '', datetime.now().strftime('%d-%m-%Y %H:%M:%S'))
        sql.insert_data([res], 'clan_users')
        return True

    @staticmethod
    def create2(user_id, id_clan):
        res = (id_clan, user_id, 0, 0, '', datetime.now().strftime('%d-%m-%Y %H:%M:%S'))
        sql.insert_data([res], 'clan_users')
        return True

    def edit(self, name, value, attr=True):
        if attr:
            setattr(self, name, value)
        sql.edit_data('id', self.id, name, value, 'clan_users')
        return value

    def dellclan(self):
        sql.delete_data(self.id, 'id', 'clan_users')
