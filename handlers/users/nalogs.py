from aiogram import flags
from aiogram.types import Message
from filters.users import flood_handler
from config import bot_name

from utils.main.bitcoin import Bitcoin
from utils.main.cash import to_str
from utils.main.moto import Moto

from utils.main.users import User
from utils.main.airplanes import Airplane
from utils.main.businesses import Business
from utils.main.cars import Car
from utils.main.houses import House

from utils.main.vertoleti import Vertolet
from utils.main.yaxti import Yaxta
from threading import Lock

lock = Lock()


@flags.throttling_key('default')
async def nalogs_handler(message: Message):
    flood = await flood_handler(message)
    if flood:
        arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[
            0].lower() else message.text.split()[2:]
        try:
            business = Business(user_id=message.from_user.id)
        except:
            business = None
        try:
            house = House(user_id=message.from_user.id)
        except:
            house = None
        try:
            car = Car(user_id=message.from_user.id)
        except:
            car = None

        try:
            yaxta = Yaxta(user_id=message.from_user.id)
        except:
            yaxta = None
        try:
            vertolet = Vertolet(user_id=message.from_user.id)
        except:
            vertolet = None
        try:
            airplane = Airplane(user_id=message.from_user.id)
        except:
            airplane = None
        try:
            moto = Moto(user_id=message.from_user.id)
        except:
            moto = None

        try:
            btc = Bitcoin(owner=message.from_user.id)
        except:
            btc = None

        xd = [business, house, car, yaxta,
              vertolet, airplane,
              moto, btc]
        nalog = sum(i.nalog for i in xd if i)

        if len(arg) == 0:
            text = '🗂️ Информация о налогах:\n'
            for imush in xd:
                if imush:
                    if imush.nalog > 0:
                        text += f'{imush.name} = {to_str(imush.nalog)}\n'
            if text == "🗂️ Информация о налогах:\n":
                text += "🗄️ Данные о налогах отсутствуют\n"
            return await message.reply(f'{text + "➖➖➖➖➖➖➖➖➖➖➖➖" if text != "🗂️ Информация о налогах:" else text}'
                                       f'\n💲 В сумме ваши налоги: {to_str(nalog)}')


@flags.throttling_key('default')
async def autonalog_handler(message: Message):
    arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[0].lower() else message.text.split()[
                                                                                                   2:]
    user = User(user=message.from_user)

    donate_source = user.donate_source
    try:
        donate_source = int(donate_source.split(',')[0])
    except AttributeError:
        return await message.reply(f'❌ Автоналоги  доступны только от привилегии <b>👾 ELITE</b>')
    if donate_source > 3:
        if user.autonalogs:
            x1 = 'Включены ☑️'
        else:
            x1 = 'Выключены 🚫'
        if len(arg) == 0:
            return await message.reply(f'Авто-налоги были успешно <b>{x1}</b>\n'
                                       )
        elif arg[0].lower().startswith('вкл'):
            now = True
            x1 = 'Включены ☑️'
            user.edit('autonalogs', now)
            return await message.reply(f'Авто-налоги были успешно <b>{x1}</b>\n'
                                       )

        elif arg[0].lower().startswith('выкл'):
            now = False
            x1 = 'Выключены 🚫'
            user.edit('autonalogs', now)
            return await message.reply(f'Авто-налоги были успешно <b>{x1}</b>\n'
                                       )
        else:
            return await message.reply(f'Ваш статус авто-налогов: <b>{x1}</b>\n'
                                       )
    else:
        return await message.reply(f'❌ Автоналоги  доступны только от привилегии <b>👾 ELITE</b>')
