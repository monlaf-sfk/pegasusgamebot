from operator import itemgetter

from aiogram import flags
from aiogram.fsm.state import State, StatesGroup

from aiogram.types import Message, CallbackQuery

from aiogram_dialog import (
    Dialog, DialogManager,
    StartMode, Window,
)
from aiogram_dialog.widgets.kbd import (ScrollingGroup, Select, SwitchTo, Button
                                        )
from aiogram_dialog.widgets.text import Format, Const

from utils.items.items import items

from utils.main.users import User


class Shop(StatesGroup):
    LIST_PAGER = State()
    INFO_PAGER = State()


items_to_sell = items.copy()
del items_to_sell[-1]

MAIN_MENU_BTN = SwitchTo(Const("Назад"), id="main", state=Shop.LIST_PAGER)


def to_str3(money: int):
    b = f'{money:,}'
    return f"{b.replace(',', '.')}$"


async def product_getter(dialog_manager: DialogManager, **_kwargs):
    user = User(id=dialog_manager.event.from_user.id)
    text = dialog_manager.dialog_data.get("text", None)
    return {
        "name": user.link,
        'text': text,
        "items": [(f'{index}. {item["name"]}{item["emoji"]} - {to_str3(item["sell_price"] * 2)}', index) for index, item
                  in items_to_sell.items()],
    }


async def on_click(callback: CallbackQuery, button: Button,
                   dialog_manager: DialogManager, item_id: str):
    item = items_to_sell[int(item_id)]
    if item['use'] == 'xp':
        text = f"{item['descriptoin']}\n\n" \
               "⬆️ Увеличивает опыт:" \
               "\n➖ Инв юз [предмет] [кол-во]"
    elif item['use'] == 'sell_count':
        text = f"{item['descriptoin']}\n\n" \
               "〽️ Дает скидку на покупку:" \
               "\n➖ Инв юз [предмет] [кол-во]"
    elif item['use'] == 'energy':
        text = f"{item['descriptoin']}\n\n" \
               "⬆️ Увеличивает энергию:" \
               "\n➖ Инв юз [предмет] [кол-во]"
    dialog_manager.dialog_data["text"] = text
    await dialog_manager.next()


shop_dialog = Dialog(
    Window(
        Format("{name} 🏪 Игровой магазин\n"
               '\nВведите: <code>Шоп купить [номер] *[кол-во]</code> чтобы приобрести предмет'),
        ScrollingGroup(

            Select(
                Format("{item[0]}"),
                id="cl",
                items="items",
                item_id_getter=itemgetter(1),
                on_click=on_click,
            ),
            width=1,
            height=5,
            id="scroll_with_pager",
        ),
        getter=product_getter,
        state=Shop.LIST_PAGER,
        disable_web_page_preview=True
    ),
    Window(
        Format("{name} {text}"),
        MAIN_MENU_BTN,
        getter=product_getter,
        state=Shop.INFO_PAGER,
        disable_web_page_preview=True

    )
)


@flags.throttling_key('default')
async def shop_list_handler(message: Message, dialog_manager: DialogManager):
    # it is important to reset stack because user wants to restart everything

    await dialog_manager.start(Shop.LIST_PAGER, mode=StartMode.NEW_STACK)
