from __future__ import annotations

from aiogram.types import Chat as OChat

from utils.main.db import sql


class Chat_wdz:
    def __init__(self, chat: OChat | int = None):
        self.source: tuple = sql.select_data(name=chat.id, title='id', row_factor=True, table='chat_wdz')
        if self.source is None:
            return None
        self.id: int = self.source[0]
        self.title: str = self.source[1]
        self.invite_link: str = self.source[2]
        self.username: str = self.source[3]
        self.switch: str = self.source[4]
        self.awards: int = self.source[5]
        self.count: int = self.source[6]

    @staticmethod
    def create(chat: OChat | int):
        res = (chat.id, chat.title, chat.invite_link,
               chat.username, 'on', 0, 0)
        sql.insert_data([res], 'chat_wdz')
        return res
