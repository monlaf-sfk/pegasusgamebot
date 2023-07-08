from operator import itemgetter

from aiogram import F, flags
from aiogram.enums import ContentType

from aiogram.types import CallbackQuery
from aiogram_dialog import (
    Dialog, DialogManager, Window
)
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.kbd import (NextPage,
                                        PrevPage, Row, ScrollingGroup, Start, Select, Button, CurrentPage
                                        )
from aiogram_dialog.widgets.media import DynamicMedia

from aiogram_dialog.widgets.text import Const, Format

from config import armory_img
from utils.main.db import sql
from utils.main.users import User
from utils.weapons.swords import Armory, ArmoryInv
from utils.weapons.weapon import weapons_item

from . import states
from .main import MAIN_MENU_BUTTON


async def product_getter(dialog_manager: DialogManager, **_kwargs):
    user = User(id=dialog_manager.event.from_user.id)
    list = [(f"{weapons_item[i[3]][i[2]]['name']}",
             f"{i[0]}:{i[2]}:{i[3]}") for i in
            sql.execute(f"SELECT * FROM armory WHERE user_id={user.id} ORDER BY weapon_id DESC", fetch=True) if
            i[5] == False]
    text = dialog_manager.dialog_data.get("text", None)
    image = MediaAttachment(
        ContentType.PHOTO, file_id=MediaId(dialog_manager.dialog_data.get("photo", armory_img['armory_menu']))
    )
    if len(list) == 0:
        return {
            'info': f"❓ {user.link}, Нету оружий",
            'text': text,
            "products": list,
            'uniqid': None,
            'notnone': False,
            'armed': dialog_manager.dialog_data.get("armed", False),
            'disassemble': dialog_manager.dialog_data.get("disassemble", False),
            'photo': image
        }
    return {
        'info': f"❓ {user.link}, Вот все доступные",
        'text': text,
        "products": list,
        'uniqid': None,
        'notnone': True,
        'armed': dialog_manager.dialog_data.get("armed", False),
        'disassemble': dialog_manager.dialog_data.get("disassemble", False),
        'photo': image

    }


@flags.throttling_key('games')
async def disassemble_action(callback: CallbackQuery, button: Button,
                             dialog_manager: DialogManager):
    uniqid = dialog_manager.dialog_data["uniqid"]
    disassemble = dialog_manager.dialog_data["disassemble"]
    try:
        armory = Armory(uniq_id=uniqid)
    except:
        await callback.answer('🔰 Даное оружие больше недоступно!\n', show_alert=True)
        return await dialog_manager.done()
    if disassemble:
        if button.widget_id == "confirm":
            disassemble = armory.parsing()
            armory_inv = ArmoryInv(callback.from_user.id)
            armory_inv.edit('fragments', armory_inv.fragments + disassemble)
            await callback.answer(f"Оружие разобрано на 💦 {disassemble} Фрагментов оружия", show_alert=True)
            dialog_manager.dialog_data["photo"] = armory_img['armory_menu']
            return await dialog_manager.back()
        else:
            dialog_manager.dialog_data["disassemble"] = False
    else:
        await callback.answer(f"⚠️ Подтвердите разбор оружия!", show_alert=True)
        dialog_manager.dialog_data["disassemble"] = True
    await dialog_manager.show()


@flags.throttling_key('games')
async def info_weapon(callback: CallbackQuery, button: Button,
                      dialog_manager: DialogManager, item: str):
    uniqid, weapon_id, type = item.split(":")
    try:
        armory = Armory(uniq_id=uniqid)
    except:
        await callback.answer('🔰 Даное оружие больше недоступно!\n', show_alert=True)
        return await dialog_manager.done()
    text = f'{armory.weapon["name"]}\n' \
           f'🔰 Прочность: {armory.durability}/{armory.weapon["max_durability"]}\n\n' \
           f'🔻мин. урон: {armory.weapon["min_attack"]} \n' \
           f'🔺макс. урон: {armory.weapon["max_attack"]}\n\n' \
           f'⚡️ Доп. шанс крита: {armory.weapon["crit_chance"]}%\n' \
           f'🩸 Доп. множитель крит. урона: + {armory.weapon["crit_multi"]}%\n'
    dialog_manager.dialog_data["text"] = text
    dialog_manager.dialog_data["armed"] = armory.armed
    dialog_manager.dialog_data["uniqid"] = uniqid
    dialog_manager.dialog_data["disassemble"] = False
    dialog_manager.dialog_data["photo"] = armory.image
    await dialog_manager.next()


PARSING_MAIN_MENU_BUTTON = Start(
    text=Const("↩️"), id="back", state=states.Parsing.MAIN,
)
scroll_parsing_armory_window = Window(
    DynamicMedia("photo"),
    Format("{info}"),
    ScrollingGroup(
        Select(
            Format("{item[0]}"),
            id="ms",
            items="products",
            item_id_getter=itemgetter(1),
            on_click=info_weapon,
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
    state=states.Parsing.MAIN,
    disable_web_page_preview=True
)
parsing_info_window = Window(
    DynamicMedia("photo"),
    Format("{text}"),
    Button(
        Const("💦 Разобрать"),
        id=f'restore',
        on_click=disassemble_action,
        when=F['disassemble'] != True
    ),
    Button(
        Const("✅ Подтвердить разбор оружия"),
        id=f'confirm',
        on_click=disassemble_action,
        when=F['disassemble'] == True
    ),
    Button(
        Const("❌ Отмена"),
        id=f'cancel',
        on_click=disassemble_action,
        when=F['disassemble'] == True
    ),
    PARSING_MAIN_MENU_BUTTON,
    getter=product_getter,
    state=states.Parsing.INFO,
    disable_web_page_preview=True
)

parsing_armory_dialog = Dialog(
    scroll_parsing_armory_window,
    parsing_info_window
)
