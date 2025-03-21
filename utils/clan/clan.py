from datetime import datetime

from utils.main.db import sql
from utils.weapons.swords import Armory, ArmoryInv

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
level_clan = {

    0: {
        'symbol': '0',
        'kazna': 50_000_000,
        'description': 100,
        'members': 5,
    },
    1: {
        'symbol': 'I',
        'kazna': 100_000_000,
        'description': 150,
        'members': 15,
    },
    2: {
        'symbol': 'II',
        'kazna': 1_000_000_000,
        'description': 200,
        'members': 25,
    },
    3: {
        'symbol': 'III',
        'kazna': 10_000_000_000,
        'description': 250,
        'members': 50,
    }
}


class Clan:
    def __init__(self, **kwargs):

        if 'clan_id' in kwargs:
            clan_id = kwargs['clan_id']
            self.source: tuple = sql.select_data(clan_id, 'id', True, 'Clans')
        elif 'owner' in kwargs:
            owner = kwargs['owner']
            self.source: tuple = sql.select_data(owner, 'owner', True, 'Clans')
        else:
            self.source = None
        if self.source is None:
            raise NameError('Not have clan')
        self.id: int = self.source[0]
        self.name: str = self.source[1]
        self.owner: int = self.source[2]
        self.rating: int = self.source[3]
        self.kazna: int = self.source[4]
        self.win: int = self.source[5]
        self.lose: int = self.source[6]
        self.members: int = self.source[7]
        self.type: int = self.source[8]
        self.description: str = self.source[9]
        self.prefix: str = self.source[10]
        self.level: int = self.source[11]
        self.invites: iter | list = self.source[12].split(',')
        self.reg_date: datetime = datetime.strptime(self.source[13], '%d-%m-%Y %H:%M:%S')
        self.last_attack: int = self.source[14]
        self.count_robs: int = self.source[15]

    @property
    def power(self):
        user_ids = sql.execute(query=f'SELECT user_id FROM ClanUsers WHERE clan_id={self.id}', commit=False, fetch=True)
        power = 0
        for user in user_ids:
            armory_inv = ArmoryInv(user[0])
            uniq_id = sql.execute(f"SELECT uniq_id FROM armory WHERE armed=True and user_id = {user[0]}", fetchone=True)
            if uniq_id:
                armory = Armory(uniq_id[0])
                damage = armory.weapon['min_attack'] + armory.weapon['max_attack']
            else:
                damage = 0
            power += armory_inv.min_damage + armory_inv.max_damage + damage
        return power

    def editmany(self, attr=True, **kwargs):
        items = kwargs.items()
        query = 'UPDATE Clans SET '
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
        res = (name, user_id, 0, 0, 0, 0, 1, 0, '', '', 0, '',
               datetime.now().strftime('%d-%m-%Y %H:%M:%S'), None, 0)
        len_title = "%s," * (len(list(res)) - 1) + "%s"

        sql.get_cursor().execute(f"INSERT INTO Clans VALUES(DEFAULT,{len_title})", res)
        sql.commit()
        return True

    def edit(self, name, value, attr=True):
        if attr:
            setattr(self, name, value)
        sql.edit_data('id', self.id, name, value, 'Clans')
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
        self.source: tuple = sql.select_data(user_id, 'user_id', True, 'ClanUsers')
        if self.source is None:
            raise Exception('Not have clan')
        self.user_id: int = self.source[0]
        self.clan_id: int = self.source[1]
        self.rating: int = self.source[2]
        self.status: int = self.source[3]
        self.reg_date: datetime = datetime.strptime(self.source[4], '%d-%m-%Y %H:%M:%S')
        self.rob_involved: bool = self.source[5]

    @property
    def power(self):
        armory_inv = ArmoryInv(self.user_id)
        uniq_id = sql.execute(f"SELECT uniq_id FROM armory WHERE armed=True and user_id = {self.user_id}",
                              fetchone=True)
        if uniq_id:
            armory = Armory(uniq_id[0])
            damage = armory.weapon['min_attack'] + armory.weapon['max_attack']
        else:
            damage = 0
        return armory_inv.min_damage + armory_inv.max_damage + damage

    def editmany(self, attr=True, **kwargs):
        items = kwargs.items()
        query = 'UPDATE ClanUsers SET '
        items_len = len(items)
        for index, item in enumerate(items):
            if attr:
                setattr(self, item[0], item[1])
            query += f'{item[0]} = {sql.item_to_sql(item[1])}'
            query += ', ' if index < items_len - 1 else ' '
        query += 'WHERE user_id = {}'.format(self.user_id)
        sql.execute(query=query, commit=True)

    @staticmethod
    def create(user_id, id_clan, status):
        res = (user_id, id_clan, 0, status, datetime.now().strftime('%d-%m-%Y %H:%M:%S'), False)
        sql.insert_data([res], 'ClanUsers')
        return True

    def edit(self, name, value, attr=True):
        if attr:
            setattr(self, name, value)
        sql.edit_data('user_id', self.user_id, name, value, 'ClanUsers')
        return value

    def dellclan(self):
        sql.delete_data(self.user_id, 'user_id', 'ClanUsers')
