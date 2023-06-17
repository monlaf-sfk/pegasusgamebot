from operator import itemgetter

from aiogram import F
from aiogram.enums import ContentType
from aiogram_dialog import (
    Dialog, DialogManager, Window
)
from aiogram_dialog.widgets.kbd import (NextPage,
                                        PrevPage, Row, ScrollingGroup, Start, Select, Button, CurrentPage,
                                        )
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format

from utils.main.cash import to_str4
from utils.main.db import sql
from utils.main.users import User
from . import states
from .category import info_lot, update_lot
from .main import MAIN_MENU_BUTTON


async def product_getter(dialog_manager: DialogManager, **_kwargs):
    user = User(id=dialog_manager.event.from_user.id)
    list = [(f"{to_str4(i[3])}🔄 • {to_str4(i[4])}💲", i[1]) for i in
            sql.execute(f"SELECT * FROM auction WHERE seller = {user.id}", False, True)]
    text = dialog_manager.dialog_data.get("text", None)
    if len(list) == 0:
        return {
            'info': f"❓ {user.link}, У вас нету активных лотов",
            'text': text,
            "products": list,
            'uuid': None,
            'price': dialog_manager.dialog_data.get("price", 1),
            'notnone': False
        }
    return {
        'info': f"❓ {user.link}, Вот все ваши активные лоты",
        'text': text,
        "products": list,
        'uuid': None,
        'price': dialog_manager.dialog_data.get("price", 1),
        'notnone': True
    }


LOTS_MAIN_MENU_BUTTON = Start(
    text=Const("↩️"), id="back", state=states.MyLots.MAIN,
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
    MAIN_MENU_BUTTON,
    getter=product_getter,
    state=states.MyLots.MAIN,
    disable_web_page_preview=True
)
lots_info_window = Window(
    StaticMedia(
        path="assets/img/diologs/auction_main.png",
        type=ContentType.PHOTO),
    Format("{text}"),
    Button(
        Const("🔄 Обновить"),
        id=f'update',
        on_click=update_lot,
        when='notnone'
    ),

    LOTS_MAIN_MENU_BUTTON,
    getter=product_getter,
    state=states.MyLots.INFO,
    disable_web_page_preview=True

)

lots_auction_dialog = Dialog(
    default_scroll_window,
    lots_info_window
)
