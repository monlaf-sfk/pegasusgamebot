from datetime import datetime, timedelta
from config import donates


def to_str(result: timedelta):
    days = result.days
    hours, remainder = divmod(result.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    res = ''
    if days > 0:
        res += f'{days} д.'
    if hours > 0:
        res += f' {hours} ч.'
    if minutes > 0:
        res += f' {minutes} м.'
    if seconds > 0:
        res += f' {seconds} с.'
    return res if res else 'Неизвестно'


def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


class Donate:
    def __init__(self, source: str):
        self.split = source.split(',')
        self.id: int = int(self.split[0])
        self.start_date: datetime = datetime.strptime(self.split[1], '%d-%m-%Y %H:%M')
        self.is_always: bool = str2bool(self.split[2])
        xd = donates[self.id]

        if self.is_always == False:
            self.to_date: int = datetime.strptime(self.split[3], '%d-%m-%Y %H:%M')

        self.name: str = xd['name']
        self.price: int = xd["price"]
        self.prefix: str = xd["emoji"]
        self.cash: int = xd['cash']
        self.percent: int = xd['percent']


class BanUser:
    def __init__(self, source: str):
        self.split = source.split(',')
        self.start_date: int = datetime.strptime(self.split[0], '%d-%m-%Y %H:%M')
        self.is_always: bool = str2bool(self.split[1])
        if self.is_always == False:
            self.to_date: datetime = datetime.strptime(self.split[2], '%d-%m-%Y %H:%M')
        self.reason: str = self.split[3:][0]
