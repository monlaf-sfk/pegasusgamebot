from aiogram.fsm.state import StatesGroup, State


class Arsenal(StatesGroup):
    MAIN = State()
    INFO = State()


class Armory(StatesGroup):
    MAIN = State()


class Craft(StatesGroup):
    MAIN = State()
    INFO = State()


class Parsing(StatesGroup):
    MAIN = State()
    INFO = State()


class Improvement(StatesGroup):
    MAIN = State()
    INFO = State()


class ShopArmory(StatesGroup):
    MAIN = State()


class Awakening(StatesGroup):
    MAIN = State()
    INFO = State()
