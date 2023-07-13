from datetime import datetime, timedelta

from utils.main.db import sql, timedelta_parse


class ClanRob:
    def __init__(self, **kwargs) -> object:
        if 'clan_id' in kwargs:
            clan_id = kwargs['clan_id']
            self.source: tuple = sql.select_data(clan_id, 'clan_id', True, 'ClanRob')

        if self.source is None:
            raise Exception('Not have ClanRob')
        self.rob_id: int = self.source[0]
        self.clan_id: int = self.source[1]
        self.index_rob: int = self.source[2]
        self.plan_rob: int = self.source[3]
        self.prepare: bool = self.source[4]
        self.balance: int = self.source[5]
        self.time_rob: datetime = self.source[6]

    def edit(self, name, value, attr=True):
        if attr:
            setattr(self, name, value)
        sql.edit_data('rob_id', self.rob_id, name, value, 'ClanRob')
        return value

    @staticmethod
    def create_rob(clan_id, index_rob, time_prepare):
        dt = datetime.now()
        time_rob = dt + timedelta_parse(time_prepare)
        res = [(clan_id, index_rob, 0, True, 0, time_rob.strftime('%d-%m-%Y %H:%M:%S'))]
        len_title = "%s," * (len(list(res[0])) - 1) + "%s"
        sql.cursor.executemany(f"INSERT INTO ClanRob VALUES (DEFAULT,{len_title})", res)
        sql.commit()
        return True
