import time
from operator import itemgetter

from aiogram import F, flags
from aiogram.enums import ContentType
from aiogram.types import CallbackQuery
from aiogram_dialog import (
    Dialog, DialogManager, Window
)
from aiogram_dialog.widgets.kbd import (NextPage,
                                        PrevPage, Row, ScrollingGroup, Start, Select, Button, CurrentPage
                                        )
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format

from loader import bot
from utils.auction import Auction
from utils.main.cash import to_str4
from utils.main.db import sql, timetostr
from utils.main.users import User
from . import states
from .main import MAIN_MENU_BUTTON


async def product_getter(dialog_manager: DialogManager, **_kwargs):
    user = User(id=dialog_manager.event.from_user.id)
    list = [(f"{to_str4(i[3])}🔄 • {to_str4(i[4])}💲", i[1]) for i in sql.get_all_data('auction')]
    text = dialog_manager.dialog_data.get("text", None)
    if len(list) == 0:
        return {
            'info': f"❓ {user.link}, Нету лотов",
            'text': text,
            "products": list,
            'uuid': None,
            'price': to_str4(dialog_manager.dialog_data.get("price", 1)),
            'notnone': False
        }
    return {
        'info': f"❓ {user.link}, Вот все доступные",
        'text': text,
        "products": list,
        'uuid': None,
        'price': to_str4(dialog_manager.dialog_data.get("price", 1)),
        'notnone': True
    }


@flags.throttling_key('games')
async def update_lot(callback: CallbackQuery, button: Button,
                     dialog_manager: DialogManager):
    item_id = dialog_manager.dialog_data.get("uuid")
    price_callback = dialog_manager.dialog_data.get("price")
    try:
        auction = Auction(str(item_id))
    except:
        await callback.answer('⚠️ Это уже не актуальный лот!', show_alert=True)
        return await dialog_manager.done()
    user = User(id=callback.from_user.id)
    price_curs = sql.execute("SELECT coin_kurs FROM other", commit=False, fetch=True)[0][0]
    price = auction.price + ((price_curs * auction.count) / 10)
    if button.widget_id == 'stavka':
        if price > int(price_callback):
            return await callback.answer('❌ Это не актуальная цена !\n'
                                         '🔄 Обновите страницу', show_alert=True)
        if price > user.balance:
            return await callback.answer('❌ Недостаточно средств для ставки!\n'
                                         f'Требуется: {price}', show_alert=True)
        if auction.seller == user.id:
            return await callback.answer('❌ Свои лоты нельзя покупать!', show_alert=True)
        if auction.costumers == user.id:
            return await callback.answer('❌ Это и так ваша ставка!', show_alert=True)
        user.edit('balance', user.balance - price)
        if auction.costumers:
            user_costumers = User(id=auction.costumers)
            user_costumers.edit('balance', user_costumers.balance + auction.price)
            await bot.send_message(chat_id=auction.costumers,
                                   text=f'Вашу ставку перебили ID: <code>{auction.uuid4}</code>\n'
                                        f'👁‍🗨 /lot_{auction.uuid4}', disable_web_page_preview=True)

        if int(time.time()) - auction.time > 840:
            auction.editmany(price=price, costumers=user.id,
                             time=auction.time + 60)
        else:
            auction.editmany(price=price, costumers=user.id)
        await callback.answer(f'✅ Вы успешно cделали ставку на {auction.uuid4} за {to_str4(price)}$',
                              disable_web_page_preview=True, show_alert=True)

    text = f'❓ Информация о лоте:\n' \
           f'🆔: <code>{auction.uuid4}</code>\n' \
           f'🔄 Количество коинов: x{to_str4(auction.count)} 🪙\n' \
           f'➖➖➖➖➖➖➖➖\n' \
           f'💲 Текущая ставка: {to_str4(auction.price)} {"<i>(Твоя ставка)</i>" if auction.costumers == callback.from_user.id else ""}\n' \
           f'🕐 Окончание через: {timetostr(auction.time + 900 - int(time.time()))}' \
           f'👁‍🗨 /lot_{auction.uuid4}'
    dialog_manager.dialog_data["text"] = text
    dialog_manager.dialog_data["price"] = price
    await dialog_manager.show()


@flags.throttling_key('games')
async def info_lot(callback: CallbackQuery, button: Button,
                   dialog_manager: DialogManager, item_id: str):
    try:
        auction = Auction(str(item_id))
    except:
        await callback.answer('⚠️ Это уже не актуальный лот!', show_alert=True)
        return await dialog_manager.done()
    text = f'❓ Информация о лоте:\n' \
           f'🆔: <code>{auction.uuid4}</code>\n' \
           f'🔄 Количество коинов: x{to_str4(auction.count)} 🪙\n' \
           f'➖➖➖➖➖➖➖➖\n' \
           f'💲 Текущая ставка: {to_str4(auction.price)} {"<i>(Твоя ставка)</i>" if auction.costumers == callback.from_user.id else ""}\n' \
           f'🕐 Окончание через: {timetostr(auction.time + 900 - int(time.time()))}' \
           f'👁‍🗨 /lot_{auction.uuid4}'
    price_curs = sql.execute("SELECT coin_kurs FROM other", commit=False, fetch=True)[0][0]
    price = auction.price + ((price_curs * auction.count) / 10)
    dialog_manager.dialog_data["uuid"] = item_id
    dialog_manager.dialog_data["price"] = price
    dialog_manager.dialog_data["text"] = text
    await dialog_manager.next()


CATEGORY_MAIN_MENU_BUTTON = Start(
    text=Const("↩️"), id="back", state=states.Category.MAIN,
)
COINS_MAIN_MENU_BUTTON = Start(
    text=Const("↩️"), id="back", state=states.Coins.MAIN,
)

navigation_menu = Window(
    StaticMedia(
        path="assets/img/diologs/auction_main.png",
        type=ContentType.PHOTO),
    Start(
        text=Const("📜 Коины"),
        id="coins",
        state=states.Coins.MAIN,
    ),
    MAIN_MENU_BUTTON,
    state=states.Category.MAIN
)

default_scroll_window = Window(
    StaticMedia(
        path="assets/img/diologs/auction_main.png",
        type=ContentType.PHOTO),
    Format("{info}"),
    ScrollingGroup(
        Select(
            Format("{item[0]}"),
            id="ms",
            items="products",
            item_id_getter=itemgetter(1),
            on_click=info_lot,
            when='notnone'
        ),
        width=1,
        height=5,
        hide_pager=True,
        id='scroll_with_pager',
    ),
    Row(
        CurrentPage(scroll="scroll_with_pager", text=Format("{current_page1}/{pages}")),
        PrevPage(
            scroll='scroll_with_pager', text=Format("◀️"),
            when=F["current_page1"] != 1
        ),
        NextPage(
            scroll='scroll_with_pager', text=Format("▶️"),
            when=F["pages"] != F["current_page1"]
        ),
        when='notnone'
    ),
    CATEGORY_MAIN_MENU_BUTTON,
    getter=product_getter,
    state=states.Coins.MAIN,
    disable_web_page_preview=True
)
coins_info_window = Window(
    StaticMedia(
        path="assets/img/diologs/auction_main.png",
        type=ContentType.PHOTO),
    Format("{text}"),
    Button(
        Format("Сделать ставку • {price}💲"),
        id=f'stavka',
        on_click=update_lot,
        when='notnone'
    ),
    Button(
        Const("🔄 Обновить"),
        id=f'update',
        on_click=update_lot,
        when='notnone'
    ),

    COINS_MAIN_MENU_BUTTON,
    getter=product_getter,
    state=states.Coins.INFO,
    disable_web_page_preview=True
)
category_auction_dialog = Dialog(
    navigation_menu

)
coins_auction_dialog = Dialog(
    default_scroll_window,
    coins_info_window
)
