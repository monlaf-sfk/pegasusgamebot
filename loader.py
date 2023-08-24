from aiogram import Bot
from aiopayok import Payok
from utils import crystal
from config import QIWI_TOKEN, crysral_login, crysral_key1, CRYPTO_TOKEN, crysral_key2, token, payok_api_key, \
    payok_api_id, payok_secret_key, shop_id, aaio_merchant_id, aaio_secret, aaio_api_key
from pyqiwip2p import QiwiP2P
from aiocryptopay import AioCryptoPay, Networks

from utils.aaio import AAIOAPI

payok = Payok(api_id=payok_api_id, api_key=payok_api_key, secret_key=payok_secret_key, shop=shop_id)
bot = Bot(token=token, parse_mode='html')
aaioapi = AAIOAPI(merchant_id=aaio_merchant_id, secret=aaio_secret, api_key=aaio_api_key)
p2p = QiwiP2P(auth_key=QIWI_TOKEN)
crypto = AioCryptoPay(token=CRYPTO_TOKEN, network=Networks.MAIN_NET)
crystal = crystal.CrystalPay(crysral_login, crysral_key1, crysral_key2)
