from uuid import uuid4, UUID

from aiogram import flags
from aiogram.enums import ContentType
from aiogram.types import Message
from aiogram_dialog import (
    Dialog, Window, LaunchMode, DialogManager, StartMode,
)
from aiogram_dialog.widgets.kbd import (
    Start,
)
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const

from config import channel_auction, channel_test
from filters.users import flood_handler
from loader import bot
from utils.auction import Auction
from utils.main.cash import to_str
from utils.main.db import sql
from utils.main.users import User
from . import states

main_auction_dialog = Dialog(
    Window(
        Const("ℹ️ Отслеживать новые лоты можно в канале с уведомлениями @pegasus_auction"),
        StaticMedia(
            path="assets/img/diologs/auction_main.png",
            type=ContentType.PHOTO),
        Start(
            text=Const("📐 Категории"),
            id="layout",
            state=states.Category.MAIN,
        ),

        Start(
            text=Const("📅 Мои лоты"),
            id="cal",
            state=states.MyLots.MAIN,
        ),
        Start(
            text=Const("💯 Мои ставки"),
            id="counter",
            state=states.MyBet.MAIN,
        ),
        state=states.Main.MAIN,
    ),
    launch_mode=LaunchMode.ROOT,
)

MAIN_MENU_BUTTON = Start(
    text=Const("↩️"),
    id="__main__",
    state=states.Main.MAIN,
)


@flags.throttling_key('games')
async def start_auction(message: Message, dialog_manager: DialogManager):
    # it is important to reset stack because user wants to restart everything
    await dialog_manager.start(states.Main.MAIN, mode=StartMode.NEW_STACK)


def is_valid_uuid(val):
    try:
        UUID(str(val))
        return True
    except ValueError:
        return False


@flags.throttling_key('games')
async def auction_lot_handler(message: Message):
    flood = await flood_handler(message)
    if flood:
        arg = message.text.split()[1:] if message.text.split()[0].lower() != 'продать' else message.text.split()

        user = User(user=message.from_user)
        if len(arg) == 0:
            return await message.reply('❌ Используйте:\n'
                                       '<code>/lot выставить коины (кол-во) </code>\n')

        elif arg[0].lower() == 'выставить':
            if arg[1].lower() in ['coins', 'коины', 'коин']:
                try:
                    count = int(arg[2])
                except:
                    return await message.reply('❌ <code>/lot выставить коины (кол-во) </code>\n!')
                if count > user.coins:
                    return await message.reply('❌ У Вас недостаточно коинов для выставления на аукцион')
                if count < 5:
                    return await message.reply('❌ Мин кол-во коинов 5')
                price_curs = sql.execute("SELECT coin_kurs FROM other", commit=False, fetch=True)[0][0]

                user.edit('coins', user.coins - count)
                uuid = str(uuid4().hex)[:15]
                await message.reply(f'✅ Вы успешно выставили Коины x{count}🪙 за {to_str((price_curs * count) / 2)}\n'
                                    f'/lot_{uuid}')
                message_id = await bot.send_message(chat_id=channel_auction, text=f'<b>⚖️ Новый лот №{uuid}</b>\n'
                                                                                  f'Предмет:<b> Коины x{count}🪙</b>\n'
                                                                                  f'Стартовая цена: <b>{to_str((price_curs * count) / 2)}</b>\n'
                                                                                  f'<b>Владелец лота:</b> {user.link}\n',
                                                    disable_web_page_preview=True
                                                    )
                Auction.add_item(seller=user.id, item_name='coins', count=count, price=(price_curs * count) / 2,
                                 uuid=uuid, message_id=message_id.message_id)
                return


        else:
            return await message.reply('❌ Используйте:\n'
                                       '<code>/lot выставить коины (кол-во)</code>\n')


@flags.throttling_key('default')
async def auction_help_handler(message: Message):
    return await message.reply("Краткое руководство по ⚖️Аукциону <a href='telegra.ph/Aukcion-05-13-6'>здесь.</a>")
