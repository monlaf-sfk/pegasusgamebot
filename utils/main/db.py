import json
import logging
import re
import time

from datetime import datetime, timedelta

import psycopg2
from psycopg2 import Error, OperationalError
from psycopg2.extras import DictCursor

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


def timedelta_parse(value):
    """
    convert input string to timedelta
    """
    value = re.sub(r"[^0-9:.]", "", value)
    if not value:
        return

    return timedelta(**{key: float(val)
                        for val, key in zip(value.split(":")[::-1],
                                            ("seconds", "minutes", "hours", "days"))
                        })


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
                                     dbname=dbname,
                                     cursor_factory=DictCursor)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users(
            id NUMERIC PRIMARY KEY,
            name text ,username text ,first_name text ,reg_date text ,
            balance NUMERIC ,bank NUMERIC,deposit NUMERIC ,
            deposit_date NUMERIC ,bonus text ,ref NUMERIC,refs NUMERIC ,
            lock BOOLEAN ,credit NUMERIC ,credit_time NUMERIC ,energy INT ,energy_time NUMERIC,
            xp NUMERIC ,sell_count INT,level NUMERIC ,job_index NUMERIC ,job_time NUMERIC , 
            work_time NUMERIC ,percent INT ,coins NUMERIC,donate_source text ,prefix text ,
            last_vidacha timestamp without time zone ,last_rob NUMERIC ,shield_count NUMERIC ,
            autonalogs BOOLEAN,ban_source TEXT ,
            state_ruletka text,nickban boolean,payban boolean,donate_videocards numeric,
            bitcoins numeric,
            limitvidach NUMERIC, blocked boolean)
        """)
        self.conn.commit()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS computers(
            owner NUMERIC PRIMARY KEY,index NUMERIC ,name text ,cash NUMERIC ,last NUMERIC ,strength NUMERIC ,progress NUMERIC)
                """)
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS airplanes(
            owner NUMERIC PRIMARY KEY,index NUMERIC ,number text ,cash NUMERIC ,last NUMERIC ,nalog NUMERIC ,fuel NUMERIC ,energy INT,time_buy text, stock_nalog NUMERIC)
        """)
        self.conn.commit()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS vertoleti(
            owner NUMERIC PRIMARY KEY,index NUMERIC ,number text ,cash NUMERIC ,last NUMERIC ,nalog NUMERIC ,fuel NUMERIC ,energy INT,time_buy text , stock_nalog NUMERIC)
        """)
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS yaxti(
            owner NUMERIC PRIMARY KEY,index NUMERIC ,number text ,cash NUMERIC ,last NUMERIC ,nalog NUMERIC ,fuel NUMERIC ,energy INT,time_buy text , stock_nalog NUMERIC)
        """)
        self.conn.commit()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS moto(
            owner NUMERIC PRIMARY KEY,index NUMERIC ,number text ,cash NUMERIC ,last NUMERIC ,nalog NUMERIC ,fuel NUMERIC ,energy INT,time_buy text, stock_nalog NUMERIC)
        """)

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS cars(
            owner NUMERIC PRIMARY KEY,index NUMERIC ,number text ,cash NUMERIC ,last NUMERIC ,nalog NUMERIC ,fuel NUMERIC ,energy INT,time_buy text, stock_nalog NUMERIC)
        """)
        self.conn.commit()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS houses(
            owner NUMERIC PRIMARY KEY, index NUMERIC ,name text ,cash NUMERIC ,last NUMERIC ,nalog NUMERIC ,arenda BOOLEAN ,stock_doxod NUMERIC, stock_nalog NUMERIC)
        """)
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS businesses(
            owner NUMERIC PRIMARY KEY,index NUMERIC ,name text ,cash NUMERIC ,last NUMERIC ,nalog NUMERIC ,arenda BOOLEAN , stock_doxod NUMERIC, stock_nalog NUMERIC)
        """)
        self.conn.commit()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS city(
            owner NUMERIC PRIMARY KEY, 
            name text ,kazna NUMERIC ,citizens NUMERIC ,happynes NUMERIC ,workers NUMERIC ,taxes INT,water jsonb ,energy jsonb ,road NUMERIC ,house jsonb, last_online timestamp without time zone )
        """)
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS marries(
            id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, 
            user1 NUMERIC ,user2 NUMERIC ,reg_date text ,balance NUMERIC ,last NUMERIC ,last_sex NUMERIC ,level INT,name text )
        """)
        self.conn.commit()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Clans(
            id BIGSERIAL PRIMARY KEY,
            name text ,owner NUMERIC ,rating NUMERIC ,kazna NUMERIC ,win NUMERIC ,lose NUMERIC ,
            members NUMERIC ,type INT ,description text,prefix text,level INT,invites text,reg_date text,
            last_attack NUMERIC,
            count_robs INTEGER)
        """)
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS ClanWars(
                    war_id SERIAL PRIMARY KEY,
                    id_first NUMERIC UNIQUE,
                    id_second NUMERIC UNIQUE,
                    name_first varchar(30),name_second varchar(30),
                    rating_first NUMERIC,rating_second NUMERIC,
                    prepare BOOL,
                    time_war timestamp without time zone
                    )
                """)
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS WarParticipants(
                            member_id NUMERIC PRIMARY KEY,
                            clan_id BIGINT,
                            war_id BIGINT,
                            power NUMERIC,
                            attacks NUMERIC,
                            cooldown NUMERIC,
                            FOREIGN KEY (clan_id) REFERENCES Clans (id),
                            FOREIGN KEY (war_id) REFERENCES ClanWars (war_id)
                        )""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS ClanWarFind(
                                    id SERIAL PRIMARY KEY,
                                    start_time TIMESTAMP NOT NULL,
                                    end_time TIMESTAMP,
                                    clan_id BIGINT,
                                    clan_name varchar(30),
                                    power NUMERIC,
                                    status varchar(30),
                                    FOREIGN KEY (clan_id) REFERENCES Clans (id)
                                )""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS ClanUsers(
            user_id NUMERIC PRIMARY KEY,
            clan_id BIGINT,rating NUMERIC ,status INT,reg_date text,
            rob_involved BOOL,
            FOREIGN KEY (clan_id) REFERENCES Clans (id))
        """)
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS items_rob (
                id NUMERIC PRIMARY KEY,
                name VARCHAR(255),
                emoji VARCHAR(10),
                sell_price NUMERIC
            );""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS user_items_rob (
                id BIGSERIAL PRIMARY KEY,
                user_id NUMERIC REFERENCES users(id),
                item_id NUMERIC REFERENCES items_rob(id),
                count INTEGER,
                UNIQUE (user_id, item_id)
            )""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS ClanRob(
                                            rob_id SERIAL PRIMARY KEY,
                                            clan_id BIGINT NOT NULL,
                                            index_rob BIGINT,
                                            plan_rob BIGINT,
                                            prepare BOOL,
                                            balance NUMERIC,
                                            time_rob TIMESTAMP,
                                            FOREIGN KEY (clan_id) REFERENCES Clans (id)
                                        )""")
        self.conn.commit()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS uah(
            owner NUMERIC PRIMARY KEY,balance NUMERIC ,level NUMERIC )
        """)
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS euro(
            owner NUMERIC PRIMARY KEY,balance NUMERIC ,level NUMERIC )
        """)
        self.conn.commit()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS bitcoin(
            owner NUMERIC PRIMARY KEY,zindex INT ,balance NUMERIC ,last NUMERIC ,videocards INT ,nalog NUMERIC ,limit_video INT, stock_doxod NUMERIC, stock_nalog NUMERIC)
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
                    zarefa numeric,credit_limit numeric,credit_percent numeric,work integer)""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS contest(
                    channel_id NUMERIC PRIMARY KEY,
                    participants_count numeric,status BOOL,
                    count_reward numeric,
                    type_reward varchar(30),
                    winners integer, text_buttton varchar(40))""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS participants(
                    user_id NUMERIC PRIMARY KEY,
                    channel_id NUMERIC)""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS other(
                    donatex2 integer,coin_kurs numeric,bonus numeric,
                    zarefa numeric,credit_limit numeric,credit_percent numeric,work integer)""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS auction(
                            seller NUMERIC,uuid4 varchar(50),item_name text,count NUMERIC,price NUMERIC,costumers NUMERIC,time NUMERIC, message_id NUMERIC)""")

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

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS quests(
                            user_id BIGINT PRIMARY KEY,
                            date_refresh timestamp without time zone ,
                            today_ids_quests INT[],
                             FOREIGN KEY (user_id) REFERENCES users (id)
                        )
                                    """)
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS quests_commit(
            uniq_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, 
            quest_id BIGINT ,
            under_quest_id BIGINT ,
            user_id BIGINT ,
            completed BOOL ,
            progress NUMERIC ,
            last_value TEXT ,
            date_completed timestamp without time zone ,
            FOREIGN KEY (user_id) REFERENCES users (id)
                         
        )
                                            """)
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS user_cases (
                user_id BIGINT REFERENCES users(id),
                case_id INT,
                count NUMERIC
                )
            """)
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS user_work_items (
                        user_id BIGINT REFERENCES users(id),
                        works_item_id INT,
                        count NUMERIC
                        )
                    """)
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS settings (
                                user_id BIGINT PRIMARY KEY,
                                pay_notifies BOOL,
                                city_notifies BOOL,
                                marry_notifies BOOL,
                                clan_notifies BOOL,
                                nick_hyperlink BOOL,
                                nick_clanteg BOOL,
                                FOREIGN KEY (user_id) REFERENCES users (id)
                                )
                            """)
        self.conn.commit()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users_offer (
                        to_whom BIGINT REFERENCES users (id),
                        from_whom BIGINT REFERENCES users (id),
                        PRIMARY KEY (to_whom, from_whom)
                    )
                                    """)
        self.conn.commit()

    def insert_data(self, data_mass, table="users"):
        try:
            len_title = "%s," * (len(list(data_mass[0])) - 1) + "%s"

            with lock:

                self.cursor.executemany(f"INSERT INTO {table} VALUES ({len_title})", data_mass)
            self.conn.commit()
            # write_admins_log('INSERT', f'SQL:INSERT INTO {table} VALUES ({data_mass})')
        except (Exception, Error, OperationalError) as error:
            write_admins_log(f'ERROR', f'{error}\nSQL:INSERT INTO {table} VALUES ({data_mass})')
            sql.get_rollback()

    def edit_data(self, title_last, last, title_new, new, table="users"):
        try:
            with lock:

                self.cursor.execute(f"UPDATE {table} SET {title_new} = %s WHERE {title_last} = %s",
                                    [(new), (last)])
                self.conn.commit()
                # write_admins_log("UPDATE", f'SQL:UPDATE {table} SET {title_new} = {new} WHERE {title_last} = {last}')
        except (Exception, Error, OperationalError) as error:
            write_admins_log(f'ERROR',
                             f'{error}\nSQL:UPDATE {table} SET {title_new} ={new} WHERE {title_last} = {last}')
            sql.get_rollback()

    def edit_data_json(self, title_last, last, jsonb_column, key_to_update, new_value, table="users"):
        try:
            with lock:
                # Load the existing JSON data from the database
                self.cursor.execute(f"SELECT {jsonb_column} FROM {table} WHERE {title_last} = %s", [(last)])
                row = self.cursor.fetchone()
                if not row:
                    return None  # Return None if the record doesn't exist

                existing_jsonb_data = row[0]

                # Convert the JSONB data to a Python dictionary
                data_dict = json.loads(existing_jsonb_data) if existing_jsonb_data else {}

                # Update the specific key with the new value
                data_dict[key_to_update] = new_value

                # Convert the updated dictionary back to JSONB format
                updated_jsonb_data = json.dumps(data_dict)

                # Update the JSONB column with the new value
                self.cursor.execute(f"UPDATE {table} SET {jsonb_column} = %s WHERE {title_last} = %s",
                                    [(updated_jsonb_data), (last)])
                self.conn.commit()
                # write_admins_log("UPDATE", f'SQL:UPDATE {table} SET {jsonb_column} = {updated_jsonb_data} WHERE {title_last} = {last}')

        except (Exception, Error, OperationalError) as error:
            write_admins_log(f'ERROR',
                             f'{error}\nSQL:UPDATE {table} SET {jsonb_column} = {updated_jsonb_data} WHERE {title_last} = {last}')
            sql.get_rollback()

    def delete_data(self, name, title_name, table="users"):
        try:
            with lock:
                self.cursor.execute(f"DELETE FROM {table} WHERE {title_name} = %s", [(name)])
                self.conn.commit()
            # write_admins_log('DELETE', f'DELETE FROM {table} WHERE {title_name} = {name}')
        except (Exception, Error, OperationalError) as error:
            write_admins_log(f'ERROR', f'{error}\nSQL:DELETE FROM {table} WHERE {title_name} = {name}')
            sql.get_rollback()

    def select_data(self, name, title, row_factor=False, table="users", column='*'):
        try:
            with lock:
                self.cursor.execute(f"SELECT {column} FROM {table} WHERE {title}=%s", [(name)])
                # write_admins_log(f'SELECT', f'SQL:SELECT {column} FROM {table} WHERE {title}={name}')

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

    def execute(self, query: str, commit: bool = False, fetch: bool = False, cursor=None, fetchone: bool = False,
                data: tuple = None):
        try:
            if cursor is None:
                cursor = self.cursor
            if data:
                cursor.execute(query, (data,))
            else:
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
