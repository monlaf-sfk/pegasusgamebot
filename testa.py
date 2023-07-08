import random
import string
import time

from datetime import datetime
from threading import Lock

import psycopg2
from psycopg2._json import Json

from utils.items.items import works_items, item_case
from utils.main.db import sql

lock = Lock()
conn = psycopg2.connect(user="postgres",
                        # пароль, который указали при установке PostgreSQL
                        password="1234",
                        host="localhost",
                        port="5432",
                        dbname="pegasus_db")
cursor = conn.cursor()
datetime_bonus = datetime(year=1920, month=1, day=1).strftime('%d-%m-%Y %H:%M:%S')


def main():
    # a=time.time()
    # cursor.execute(f"SELECT id, first_name, name, username, deposit+bank+balance, prefix FROM users ORDER BY deposit+bank+balance DESC LIMIT 200;")
    # print(cursor.fetchall())
    # print(time.time()-a)
    for i in range(10000):
        now_date = datetime.now()
        reg_date = now_date.strftime('%d-%m-%Y %H:%M:%S')
        username = ''.join(
            random.choice(string.ascii_letters + '0123456789_') for _ in range(random.randint(6, 10))).lower()
        first_name = ''.join(
            random.choice(string.ascii_letters + '0123456789_') for _ in range(random.randint(6, 10))).lower()
        id = i + random.randint(1000000, 99999999999999)

        res = (id, None, username, first_name, reg_date, False, 5000, 0, 0, Json(works_items), None,
               datetime_bonus, None, 0, False, 0, None, 10, None,
               0, 0, 0, 0, None, None, 0, 0, None, None, None, 0.0, 0, False, None, 100, Json(item_case), None, False,
               False, 0, 0,
               0, False, True)
        len_title = "%s," * (len(list(res)) - 1) + "%s"

        with lock:
            res2 = (id, 1, 0, time.time(), 0, 0, 1000, 17_500, 0.5)
            len_title2 = "%s," * (len(list(res2)) - 1) + "%s"
            cursor.execute(f"INSERT INTO bitcoin VALUES ({len_title2})", res2)
            cursor.execute(f"INSERT INTO users VALUES ({len_title})", res)
            conn.commit()
        print(i)


if __name__ == '__main__':
    main()
