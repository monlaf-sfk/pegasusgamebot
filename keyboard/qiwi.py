from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def buy_menu(isUrl=True, url="", bill=""):
    qiwiMenu = InlineKeyboardBuilder()
    if isUrl:
        btnUrlQIwi = InlineKeyboardButton(text="🔗 Ссылка на оплату", url=url)
        qiwiMenu.add(btnUrlQIwi)
    btnCheckQIwi = InlineKeyboardButton(text="✔️ Проверить оплату", callback_data='check2_' + bill)
    qiwiMenu.add(btnCheckQIwi)
    qiwiMenu.adjust(1)
    return qiwiMenu


def buy_menu_crystal(isUrl=True, url="", payment_id=0, amount=0):
    crystalMenu = InlineKeyboardBuilder()
    if isUrl:
        btnUrlCrystal = InlineKeyboardButton(text="🔗 Ссылка на оплату", url=url)
        crystalMenu.add(btnUrlCrystal)
    btnCheckCrystal = InlineKeyboardButton(text="✔️ Проверить оплату", callback_data=f'crystal:{payment_id}:{amount}')
    crystalMenu.add(btnCheckCrystal)
    crystalMenu.adjust(1)
    return crystalMenu


def buy_menu_crypto(isUrl=True, url="", invoice_id=0, amount=0):
    cryptoMenu = InlineKeyboardBuilder()
    if isUrl:
        btnUrlCrypto = InlineKeyboardButton(text="🔗 Ссылка на оплату", url=url)
        cryptoMenu.add(btnUrlCrypto)
    btnCheckCrypto = InlineKeyboardButton(text="✔️ Проверить оплату", callback_data=f'crypto:{invoice_id}:{amount}')
    cryptoMenu.add(btnCheckCrypto)
    cryptoMenu.adjust(1)
    return cryptoMenu


def buy_menu_payok(isUrl=True, url="", invoice_id=0):
    payokMenu = InlineKeyboardBuilder()
    if isUrl:
        btnUrlCrypto = InlineKeyboardButton(text="🔗 Ссылка на оплату", url=url)
        payokMenu.add(btnUrlCrypto)
    btnCheckpayok = InlineKeyboardButton(text="✔️ Проверить оплату", callback_data=f'payok:{invoice_id}')
    payokMenu.add(btnCheckpayok)
    payokMenu.adjust(1)
    return payokMenu
