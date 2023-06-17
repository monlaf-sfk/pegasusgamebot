from aiogram.fsm.state import StatesGroup, State


class Category(StatesGroup):
    MAIN = State()
    COINS = State()


class Coins(StatesGroup):
    MAIN = State()
    INFO = State()


class Main(StatesGroup):
    MAIN = State()


class MyLots(StatesGroup):
    MAIN = State()
    INFO = State()


class MyBet(StatesGroup):
    MAIN = State()
    INFO = State()


class InfoLot(StatesGroup):
    MAIN = State()
