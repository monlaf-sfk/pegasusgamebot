import random
import string

from datetime import datetime
from threading import Lock

import psycopg2

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
    for i in range(50_000):
        now_date = datetime.now()
        reg_date = now_date.strftime('%d-%m-%Y %H:%M:%S')
        username = ''.join(
            random.choice(string.ascii_letters + '0123456789_') for _ in range(random.randint(6, 10))).lower()
        first_name = ''.join(
            random.choice(string.ascii_letters + '0123456789_') for _ in range(random.randint(6, 10))).lower()

        res = (
            i + random.randint(1000000, 99999999), None, username, first_name, reg_date, False, 5000, 0, 0, '', '',
            None,
            datetime_bonus, None, 0, False, 0, None, 10, None,
            0, 0, 0, 0, None, None, 0, 0, None, None, None, 0.0, 0, False, 0, False, 100, '', 0, None, False, False, 0,
            0,
            0)

        len_title = "%s," * (len(list(res)) - 1) + "%s"

        with lock:
            cursor.execute(f"INSERT INTO users VALUES ({len_title})", res)
            conn.commit()
        print(i)


if __name__ == '__main__':
    main()
