from __future__ import annotations

import decimal
import random
import numpy as np
from utils.main.cash import transform2

from utils.photos.photos import get_photo, set_photo
from utils.main.db import sql

actions = ['👊🏿 Вьебали босса с кулачины', '💩 Обосрали босса',
           '🗡️ Выебали босса 1х1 в бравлике', '🤸🏼‍♂️ Ебанули шпагат боссу',
           '🪝 Схватили босса за яйца', '🥲 Пукнули с подливой', '🤸 Нагнул босса и выебал в очко']


class Boss:
    def __init__(self, id: int):

        self.source: tuple = sql.select_data(name=id, title='id',
                                             row_factor=True, table='bosses')
        if self.source is None:
            raise Exception('Bosse did not exists')
        self.bosse = bosses[self.source[0]]
        self.id = self.source[0]
        self.emoji = self.bosse['emoji']
        self.name = self.bosse['name']
        self.hp = self.source[1] if self.source[1] > 0 else 0
        self.img = 'bosses/' + self.bosse['img']
        self.begin_hp = self.bosse['begin_hp']
        self.dodge = self.bosse['dodge']
        self.protect = self.bosse['protect']

    @property
    def photo(self):
        return get_photo(self.img)

    @photo.setter
    def photo(self, value):
        set_photo(self.img, value)

    @property
    def text(self):
        return f'{self.emoji} <b>{self.name}</b>\n' \
               f'💓 Здоровье: <b>{f"{transform2(self.hp)}/{transform2(self.begin_hp)}" if self.hp > 0 else "Босс повержен"}</b> ❤️‍🩹\n' \
               f'💨 Уклонение: <b>{self.dodge}%</b>\n' \
               f'🛡 Защита: <b>{self.protect}%</b>\n\n'

    def edit(self, name, value, attr=True, table="bosses"):
        if attr:
            setattr(self, name, value)
        sql.edit_data('id', self.source[0], name, value, table=table)
        return value

    async def push(self, weapon: dict = None, min_damage: int = 1, max_damage: int = 1):

        x = random.randint(min_damage, max_damage)
        if weapon:
            x += random.randint(weapon["min_attack"], weapon["max_attack"])
            crit_chance = np.random.choice([1, 2], 1,
                                           p=[1 - weapon["crit_chance"] * 0.01, weapon["crit_chance"] * 0.01])[0]

            if crit_chance == 2:
                x += x * weapon["crit_multi"] * 0.01

        if self.protect > 0:
            x = round(x - (x / self.protect * 0.01))

        if self.dodge > 0:
            dodge = np.random.choice([1, 2], 1,
                                     p=[1 - (self.dodge * 0.01), self.dodge * 0.01])[0]
            if dodge == 2:
                return {
                    'damage': 0
                }

        self.edit('hp', decimal.Decimal(self.hp) - decimal.Decimal(x) if decimal.Decimal(self.hp) - decimal.Decimal(
            x) >= 0 else 0)
        return {
            'damage': x
        }


bosses = {
    1: {'name': 'Паук Аркадий',
        'emoji': '🕷️',
        'begin_hp': 200000,
        'img': 'spider',
        'dodge': 0,
        'protect': 0
        },
    2: {'name': 'Монстр Глубин',
        'emoji': '🦈',
        'begin_hp': 300000,
        'img': 'putin_shark',
        'dodge': 5,
        'protect': 0
        },
    3: {'name': 'Елена Малышева',
        'emoji': '👩‍⚕️',
        'begin_hp': 350000,
        'img': 'elena',
        'dodge': 5,
        'protect': 10
        },
    4: {'name': 'Коллектор',
        'emoji': '🐉',
        'begin_hp': 350000,
        'img': 'putin',
        'dodge': 10,
        'protect': 20
        },
    5: {'name': 'Uchiha Trump',
        'emoji': '👁️',
        'begin_hp': 260000,
        'img': 'trump',
        'dodge': 15,
        'protect': 0
        },
    6: {'name': 'Обэмэ',
        'emoji': '👶🏼',
        'begin_hp': 300000,
        'img': 'halk_obama',
        'dodge': 5,
        'protect': 50
        },
}
