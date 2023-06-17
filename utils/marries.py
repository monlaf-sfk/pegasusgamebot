from __future__ import annotations

from datetime import datetime

from utils.main.db import sql


def all_marries():
    all_marries_ = [i[1] for i in sql.get_all_data('marries')]
    return all_marries_


class Marry:
    def __init__(self, **kwargs):
        if 'user_id' in kwargs:

            user_id = kwargs['user_id']
            self.source = sql.execute(f'SELECT * FROM marries WHERE (user1 = {user_id}) OR (user2 = {user_id})',
                                      False,
                                      True)
            try:
                self.source = self.source[-1]
            except:
                self.source = None
        if self.source is None:
            raise Exception('NotFoundMarry')

        self.id: int = self.source[0]
        self.user1: int = self.source[1]
        self.user2: int = self.source[2]
        self.reg_date: datetime = datetime.strptime(self.source[3], '%d-%m-%Y %H:%M:%S')
        self.balance: int = self.source[4]
        self.last: int | None = self.source[5]
        self.last_sex: int | None = self.source[6]
        self.level: int = self.source[7]
        self.name: str | None = self.source[8]

    def edit(self, name, value, attr=True):
        if attr:
            setattr(self, name, value)
        sql.edit_data('user1', self.user1, name, value, 'marries')

    def editmany(self, attr=True, **kwargs):
        items = kwargs.items()
        query = 'UPDATE marries SET '
        items_len = len(items)
        for index, item in enumerate(items):
            if attr:
                setattr(self, item[0], item[1])
            query += f'{item[0]} = {sql.item_to_sql(item[1])}'
            query += ', ' if index < items_len - 1 else ' '
        query += 'WHERE user1 = {}'.format(self.user1)
        sql.execute(query=query, commit=True)

    @staticmethod
    def create(user1: int, user2: int):
        res = (user1, user2, datetime.now().strftime('%d-%m-%Y %H:%M:%S'), 500, None, None, 1, '')
        sql.get_cursor().execute("INSERT INTO marries VALUES(DEFAULT,%s,%s,%s,%s,%s,%s,%s,%s)", res)

        return res

    def delete(self):
        sql.delete_data(self.user1, 'user1', 'marries')
