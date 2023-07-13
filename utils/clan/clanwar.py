from datetime import datetime

from utils.main.db import sql


class ClanWarFind:
    def __init__(self, **kwargs):
        if 'clan_id' in kwargs:
            clan_id = kwargs['clan_id']
            self.source: tuple = sql.execute(
                f"SELECT * FROM ClanWarFind WHERE clan_id = {clan_id} AND status = 'FINDING'", fetchone=True)
        if self.source is None:
            raise Exception('Not have ClanWarFind')
        self.id: int = self.source[0]
        self.start_time: datetime = self.source[1]
        self.end_time: datetime = self.source[2]
        self.clan_id: int = self.source[3]
        self.clan_name: int = self.source[4]
        self.power: int = self.source[5]
        self.status: int = self.source[6]

    @staticmethod
    def find_to_war(clan_id, clan_name, power, status):
        res = (datetime.now().strftime('%d-%m-%Y %H:%M:%S'), None,
               clan_id, clan_name, power, status)
        len_title = "%s," * (len(list(res)) - 1) + "%s"
        sql.get_cursor().execute(f"INSERT INTO ClanWarFind VALUES(DEFAULT,{len_title})", res)
        sql.commit()
        return True


class ClanWarMember:
    def __init__(self, **kwargs):
        if 'member_id' in kwargs:
            member_id = kwargs['member_id']
            self.source: tuple = sql.select_data(member_id, 'member_id', True, 'WarParticipants')
        if self.source is None:
            raise Exception('Not have clans_wars_member')
        self.member_id: int = self.source[0]
        self.clan_id: int = self.source[1]
        self.war_id: int = self.source[2]
        self.power: int = self.source[3]
        self.attacks: int = self.source[4]
        self.cooldown: int = self.source[5]

    def edit(self, name, value, attr=True):
        if attr:
            setattr(self, name, value)
        sql.edit_data('member_id', self.member_id, name, value, 'WarParticipants')
        return value

    @staticmethod
    def insert_to_war(member_id, clan_id, war_id, power):

        res = (member_id, clan_id, war_id, power, 0, None)
        sql.insert_data([res], 'WarParticipants')
        return True


class ClanWar:
    def __init__(self, **kwargs) -> object:
        if 'clan_id' in kwargs:
            clan_id = kwargs['clan_id']
            self.source: tuple = sql.execute(
                f'SELECT * FROM ClanWars WHERE (id_first = {clan_id}) OR (id_second = {clan_id})',
                fetch=True)

            try:
                self.source = self.source[-1]
            except:
                self.source = None

        if self.source is None:
            raise Exception('Not have clan war')
        self.war_id: int = self.source[0]
        self.id_first: int = self.source[1]
        self.id_second: int = self.source[2]
        self.name_first: str = self.source[3]
        self.name_second: str = self.source[4]
        self.rating_first: int = self.source[5]
        self.rating_second: int = self.source[6]
        self.prepare: bool = self.source[7]
        self.time_war: datetime = self.source[8]

    def edit(self, name, value, attr=True):
        if attr:
            setattr(self, name, value)
        sql.edit_data('war_id', self.war_id, name, value, 'ClanWars')
        return value
