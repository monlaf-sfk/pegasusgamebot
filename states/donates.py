from aiogram.fsm.state import State, StatesGroup


class CryptoBot(StatesGroup):
    start = State()


class CrystalPay(StatesGroup):
    start = State()


class PayokPay(StatesGroup):
    start = State()


class AaioPay(StatesGroup):
    start = State()
