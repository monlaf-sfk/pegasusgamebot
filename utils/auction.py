import time

from utils.main.db import sql


def all_item():
    all_item_ = [str(i[1]).lower() for i in sql.get_all_data('auction')]
    return all_item_


class Auction:
    def __init__(self, uuid):
        self.source = sql.execute(f"SELECT * FROM auction WHERE uuid4 ='{uuid}'", False, True)
        if len(self.source) == 0:
            raise Exception('Лот не найден!')

        self.source = self.source[-1]
        self.seller: int = self.source[0]
        self.uuid4: str = str(self.source[1])
        self.item_name: str = self.source[2]
        self.count: int = self.source[3]
        self.price: int = int(self.source[4])
        self.costumers: int = self.source[5]
        self.time: int = int(self.source[6])
        self.message_id: int = self.source[7]

    @staticmethod
    def add_item(seller, item_name, count, price, uuid, message_id):
        res = (seller, uuid, item_name, count, price, None, time.time(), message_id)
        sql.insert_data([res], 'auction')
        return True

    def edit(self, name, value, attr=True):
        if attr:
            setattr(self, name, value)
        sql.edit_data('uuid4', self.uuid4, name, value)
        return value

    def editmany(self, attr=True, **kwargs):

        items = kwargs.items()
        query = "UPDATE auction SET "
        items_len = len(items)
        for index, item in enumerate(items):
            if attr:
                setattr(self, item[0], item[1])
            query += f"{item[0]} = {sql.item_to_sql(item[1])}"
            query += ", " if index < items_len - 1 else " "
        query += "WHERE uuid4 = '{}'".format(self.uuid4)
        sql.execute(query=query, commit=True)
