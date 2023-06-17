import logging

from datetime import datetime

import psycopg2
from psycopg2 import Error, OperationalError

import config
from config import log

from threading import Lock, Thread

if log:
    lastdate = datetime.now().strftime("%d.%m.%y")
    logger = logging.getLogger('log_db')
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(f'assets/logs/{lastdate}.log', mode='a', encoding='utf-8')
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '[%(asctime)s] %(message)s', datefmt='%H:%M:%S')
    fh.setFormatter(formatter)
    logger.addHandler(fh)


def new_file():
    if not log:
        return
    global lastdate, fh

    lastdate = datetime.now().strftime("%d.%m.%y")
    try:
        logger.removeHandler(fh)
    except:
        pass
    fh = logging.FileHandler(f'assets/logs/{lastdate}.log', mode='a', encoding='utf-8')
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '[%(asctime)s] %(message)s', datefmt='%H:%M:%S')
    fh.setFormatter(formatter)
    logger.addHandler(fh)


def logs_admin(action: str, text: str):
    if lastdate != datetime.now().strftime("%d.%m.%y") or logger is None:
        new_file()

    logger.info(f'({action}): {text}')


def write_admins_log(action: str, text: str):
    if not log:
        return

    Thread(target=logs_admin, args=(action, text)).start()


lock = Lock()


def timetomin(result: int):
    result = 3600 - result
    minutes = int((result // 60) % 60)
    return f'{minutes} мин.'


def timetostr(result: int):
    a = int(result // 3600)
    b = int((result % 3600) // 60)
    c = int((result % 3600) % 60)

    res = ''
    if a > 0:
        res += f'{a} ч.'
    if b > 0:
        res += f' {b} м.'
    if c > 0:
        res += f' {c} с.'
    return res if res else 'Неизвестно'


class Lsql:
    def __init__(self, user: str, password, host, port: int, dbname: str):

        self.conn = psycopg2.connect(user=user,
                                     # пароль, который указали при установке PostgreSQL
                                     password=password,
                                     host=host,
                                     port=port,
                                     dbname=dbname)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users(
            id NUMERIC PRIMARY KEY,
            name text ,username text ,first_name text ,reg_date text ,
            notifies BOOLEAN ,balance NUMERIC ,bank INT,deposit NUMERIC ,
            items text ,deposit_date NUMERIC ,bonus text ,ref NUMERIC,refs NUMERIC ,
            lock BOOLEAN ,credit NUMERIC ,credit_time NUMERIC ,energy INT ,energy_time NUMERIC,
            xp NUMERIC ,sell_count INT,level NUMERIC ,job_index NUMERIC ,job_time NUMERIC , 
            work_time NUMERIC ,percent INT ,coins NUMERIC,donate_source text ,prefix text ,
            last_vidacha timestamp without time zone ,last_rob NUMERIC ,shield_count NUMERIC ,
            autonalogs BOOLEAN,ban_source TEXT ,health NUMERIC  ,cases text,
            state_ruletka text,nickban boolean,payban boolean,donate_videocards numeric,
            bitcoins numeric,
            limitvidach NUMERIC, clan_teg boolean)
        """)
        self.conn.commit()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS airplanes(
            index NUMERIC ,number text ,cash NUMERIC ,last NUMERIC ,nalog NUMERIC ,fuel NUMERIC ,energy INT,owner NUMERIC PRIMARY KEY,time_buy text)
        """)
        self.conn.commit()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS vertoleti(
            index NUMERIC ,number text ,cash NUMERIC ,last NUMERIC ,nalog NUMERIC ,fuel NUMERIC ,energy INT,owner NUMERIC PRIMARY KEY,time_buy text)
        """)
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS yaxti(
            index NUMERIC ,number text ,cash NUMERIC ,last NUMERIC ,nalog NUMERIC ,fuel NUMERIC ,energy INT,owner NUMERIC PRIMARY KEY,time_buy text)
        """)
        self.conn.commit()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS moto(
            index NUMERIC ,number text ,cash NUMERIC ,last NUMERIC ,nalog NUMERIC ,fuel NUMERIC ,energy INT,owner NUMERIC PRIMARY KEY,time_buy text)
        """)

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS cars(
            index NUMERIC ,number text ,cash NUMERIC ,last NUMERIC ,nalog NUMERIC ,fuel NUMERIC ,energy INT,owner NUMERIC PRIMARY KEY,time_buy text)
        """)
        self.conn.commit()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS houses(
            index NUMERIC ,name text ,cash NUMERIC ,last NUMERIC ,nalog NUMERIC ,arenda BOOLEAN ,owner NUMERIC PRIMARY KEY)
        """)
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS businesses(
            index NUMERIC ,name text ,cash NUMERIC ,last NUMERIC ,nalog NUMERIC ,arenda BOOLEAN ,owner NUMERIC PRIMARY KEY)
        """)
        self.conn.commit()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS city(
            owner NUMERIC PRIMARY KEY, 
            name text ,kazna NUMERIC ,citizens NUMERIC ,happynes NUMERIC ,workers NUMERIC ,taxes INT,water text ,energy text ,road NUMERIC ,house text )
        """)
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS marries(
            id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, 
            user1 NUMERIC ,user2 NUMERIC ,reg_date text ,balance NUMERIC ,last NUMERIC ,last_sex NUMERIC ,level INT,name text )
        """)
        self.conn.commit()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS clans(
            id NUMERIC PRIMARY KEY,
            name text ,owner NUMERIC ,rating NUMERIC ,kazna NUMERIC ,win NUMERIC ,lose NUMERIC ,members NUMERIC ,type INT ,power NUMERIC,prefix text,level INT,invites text,reg_date text,last_attack NUMERIC)
        """)
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS clan_users(
            id_clan NUMERIC,id NUMERIC,rating NUMERIC ,status INT,items text,reg_date text)
        """)
        self.conn.commit()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS uah(
            owner NUMERIC PRIMARY KEY,balance NUMERIC ,level NUMERIC )
        """)
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS euro(
            owner NUMERIC PRIMARY KEY,balance NUMERIC ,level NUMERIC )
        """)
        self.conn.commit()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS bitcoin(
            owner NUMERIC PRIMARY KEY,zindex INT ,balance NUMERIC ,last NUMERIC ,videocards INT ,nalog NUMERIC ,limit_video INT )
        """)
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS promocodes(
            id NUMERIC PRIMARY KEY,
            name text ,activations NUMERIC,users text ,status BOOLEAN ,summ NUMERIC ,xd INT)
        """)
        self.conn.commit()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS chats(
            id NUMERIC PRIMARY KEY,
            title text ,photo text,invite_link text ,username text )
        """)
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS chat_wdz(
            id NUMERIC PRIMARY KEY,
            title text ,invite_link text ,username text , switch text , awards NUMERIC , count NUMERIC )
        """)
        self.conn.commit()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS minesweeper(
            game_id uuid, user_id NUMERIC, field_size INT, victory BOOLEAN 
        )""")
        self.conn.commit()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS other(
                    donatex2 integer,coin_kurs numeric,bonus numeric,
                    zarefa numeric,credit_limit numeric,credit_percent numeric,work integer,
                    type_gift integer,summa numeric,count numeric,switch text )""")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS auction(
                            seller NUMERIC,uuid4 varchar(50),item_name text,count NUMERIC,price NUMERIC,costumers NUMERIC,time NUMERIC, message_id NUMERIC)""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS computers(
                    index NUMERIC ,name text ,cash NUMERIC ,last NUMERIC ,strength NUMERIC ,progress NUMERIC,owner NUMERIC PRIMARY KEY)
                """)
        self.conn.commit()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS bosses(
                            id INT PRIMARY KEY,
                            hp NUMERIC)
                        """)
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS user_bosses(
                            user_id BIGINT ,
                            boss_id INT,
                            damage NUMERIC,
                            count_hit INT,
                            reset_count timestamp without time zone)
                        """)
        self.conn.commit()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS armory(
                            uniq_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, 
                            user_id BIGINT,
                            weapon_id INT,
                            type varchar(20),
                            durability INT,
                            armed BOOL)
                                """)
        self.conn.commit()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS armory_inv(
                            user_id BIGINT PRIMARY KEY,
                            min_damage NUMERIC,
                            max_damage NUMERIC,
                            tokens NUMERIC,
                            repair_kit NUMERIC,
                            fragments NUMERIC
                            )
                                """)
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS gift_users(
                            user_id NUMERIC)
                            """)
        self.conn.commit()

    def insert_data(self, data_mass, table="users"):
        try:
            len_title = "%s," * (len(list(data_mass[0])) - 1) + "%s"
            with lock:

                self.cursor.executemany(f"INSERT INTO {table} VALUES ({len_title})", data_mass)
                self.conn.commit()
                # write_admins_log('INSERT',f'SQL:INSERT INTO {table} VALUES ({data_mass})')
        except (Exception, Error, OperationalError) as error:
            write_admins_log(f'ERROR', f'{error}\nSQL:INSERT INTO {table} VALUES ({data_mass})')
            sql.get_rollback()

    def edit_data(self, title_last, last, title_new, new, table="users"):
        try:
            with lock:

                self.cursor.execute(f"UPDATE {table} SET {title_new} = %s WHERE {title_last} = %s",
                                    [(new), (last)])
                self.conn.commit()
                # write_admins_log("UPDATE",f'SQL:UPDATE {table} SET {title_new} ={new} WHERE {title_last} = {last}')
        except (Exception, Error, OperationalError) as error:
            write_admins_log(f'ERROR',
                             f'{error}\nSQL:UPDATE {table} SET {title_new} ={new} WHERE {title_last} = {last}')
            sql.get_rollback()

    def delete_data(self, name, title_name, table="users"):
        try:
            with lock:
                self.cursor.execute(f"DELETE FROM {table} WHERE {title_name} = %s", [(name)])
                self.conn.commit()
            # write_admins_log('DELETE',f'DELETE FROM {table} WHERE {title_name} = {name}')
        except (Exception, Error, OperationalError) as error:
            write_admins_log(f'ERROR', f'{error}\nSQL:DELETE FROM {table} WHERE {title_name} = {name}')
            sql.get_rollback()

    def select_data(self, name, title, row_factor=False, table="users", column='*'):
        try:
            with lock:
                self.cursor.execute(f"SELECT {column} FROM {table} WHERE {title}=%s", [(name)])
                # write_admins_log(f'ERROR', f'SQL:SELECT {column} FROM {table} WHERE {title}={name}')

            if row_factor:

                with lock:
                    return self.cursor.fetchone()
            else:
                with lock:
                    return self.cursor.fetchall()
        except (Exception, Error, OperationalError) as error:
            write_admins_log(f'ERROR', f'{error}\nSQL:SELECT {column} FROM {table} WHERE {title}={name}')
            sql.get_rollback()

    def search(self, type_search, name_search, table="users"):
        try:
            with lock:
                self.cursor.execute(f"SELECT * FROM {table} WHERE {type_search} LIKE {name_search}")
                return self.cursor.fetchall()
        except (Exception, Error, OperationalError) as error:
            write_admins_log(f'ERROR', f'{error}\nSQL:SELECT * FROM {table} WHERE {type_search} LIKE {name_search}')

    def get_all_data(self, table="users"):
        try:
            with lock:
                self.cursor.execute(f"SELECT * FROM {table}")
                return self.cursor.fetchall()
        except (Exception, Error, OperationalError) as error:
            write_admins_log(f'ERROR', f'{error}\nSQL:SELECT * FROM {table}')
            sql.get_rollback()

    def get_only_data(self, table="users", column='*'):
        try:
            with lock:
                self.cursor.execute(f"SELECT {column} FROM {table}")
                return self.cursor.fetchone()
        except (Exception, Error, OperationalError) as error:
            write_admins_log(f'ERROR', f'{error}\nSQL:SELECT {column} FROM {table}')
            sql.get_rollback()

    def execute(self, query: str, commit: bool = False, fetch: bool = False, cursor=None, fetchone: bool = False):
        try:
            if cursor is None:
                cursor = self.cursor
            with lock:

                cursor.execute(query)
            if commit:
                with lock:
                    self.conn.commit()
            with lock:
                # write_admins_log(f'EXECUTE', f'{query}')
                return cursor.fetchall() if fetch else cursor.fetchone() if fetchone else None
        except (Exception, Error, OperationalError) as error:
            write_admins_log(f'ERROR', f'{error}\nSQL:{query}')
            sql.get_rollback()

    def executescript(self, query: str, commit: bool = False, fetch: bool = False, cursor=None):
        try:
            if cursor is None:
                cursor = self.cursor
            with lock:
                cursor.execute(query)
            if commit:
                with lock:
                    self.conn.commit()
            with lock:
                # write_admins_log(f'EXECUTEMANY', f'{query}')
                return cursor.fetchall() if fetch else None
        except (Exception, Error, OperationalError) as error:
            write_admins_log(f'ERROR', f'{error}\nSQL:{query}')
            sql.get_rollback()

    def executescriptSql(self, query: str, commit: bool = False, fetch: bool = False, cursor=None):
        try:
            if cursor is None:
                cursor = self.cursor
            with lock:
                cursor.execute(query)

            if commit:
                with lock:
                    self.conn.commit()
            with lock:
                # write_admins_log(f'EXECUTEMANY', f'{query}')
                return cursor.fetchall() if fetch else 'REQUEST COMPLETED'
        except (Exception, Error, OperationalError) as error:
            write_admins_log(f'ERROR', f'{error}')
            sql.get_rollback()
            return error

    def commit(self):
        with lock:
            self.conn.commit()

    def get_cursor(self):
        return self.cursor

    def get_rollback(self):
        return self.conn.rollback()

    def item_to_sql(self, item):
        if type(item) == str:
            return f"'{item}'"
        elif type(item) == bool:
            return 'TRUE' if item else 'FALSE'
        elif item is None:
            return 'NULL'
        else:
            return item


sql = Lsql(config.USER_DB, config.PASSWORD_DB, config.HOST_DB, config.PORT_DB, config.NAME_DB)
