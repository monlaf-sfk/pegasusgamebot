import json
from operator import itemgetter
from typing import Any

from aiogram import F, flags
from aiogram.enums import ContentType

from aiogram.types import CallbackQuery
from aiogram_dialog import (
    Dialog, DialogManager, Window
)
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.kbd import (NextPage,
                                        PrevPage, Row, ScrollingGroup, Start, Select, Button, CurrentPage, Column
                                        )
from aiogram_dialog.widgets.media import DynamicMedia

from aiogram_dialog.widgets.text import Const, Format

from config import armory_img
from utils.main.users import User
from utils.weapons.swords import ArmoryInv, Armory
from . import states
from .main import MAIN_MENU_BUTTON


async def product_getter(dialog_manager: DialogManager, **_kwargs):
    user = User(id=dialog_manager.event.from_user.id)
    image = MediaAttachment(
        ContentType.PHOTO, file_id=MediaId(dialog_manager.dialog_data.get("photo", armory_img['armory_menu']))
    )
    with open(file='utils/weapons/weapon.json', mode='r', encoding="utf-8") as file:
        dicts = json.load(file)
    list = [(f"{i}", f"{i}") for i in dicts if i != 'intermediate']
    text = dialog_manager.dialog_data.get("text", None)

    return {
        'info': f"❓ {user.link}, Вот все доступные",
        'text': text,
        "products": list,
        "weapons": dialog_manager.dialog_data.get("weapons", None),
        'photo': image
    }


@flags.throttling_key('games')
async def weapon_action(callback: CallbackQuery, button: Button,
                        dialog_manager: DialogManager, widget: Any):
    type, weapon_id, price = widget.split(":")
    armory_inv = ArmoryInv(callback.from_user.id)
    if armory_inv.fragments > int(price):
        Armory.create_armory(
            user_id=callback.from_user.id,
            id_weapons=weapon_id,
            type=type)
        armory_inv.edit('fragments', armory_inv.fragments - int(price))
        weapon = Armory.get_json(type, weapon_id)
        await callback.answer(f"Вы успешно скрафтили {weapon['name']} x1", show_alert=True)
    else:
        await callback.answer(f"Не достаточно фрагментов для крафта!", show_alert=True)
    with open(file='utils/weapons/weapon.json', mode='r', encoding="utf-8") as file:
        dicts = json.load(file, encoding="utf-8")[type]
    dicts = dicts
    weapon = dicts['1']
    text = f'{weapon["name"]}\n' \
           f'🔰 Прочность: {weapon["durability"]}/{weapon["max_durability"]}\n\n' \
           f'🔻мин. урон: {weapon["min_attack"]} \n' \
           f'🔺макс. урон: {weapon["max_attack"]}\n\n' \
           f'⚡️ Доп. шанс крита: {weapon["crit_chance"]}%\n' \
           f'🩸 Доп. множитель крит. урона: + {weapon["crit_multi"]}%\n\n' \
           f'--------------------\n'
    weapons = []
    index = 1
    weapons.append(('', f"{type}:{index}:{dicts[f'{index}']['disassemble'] * 2}"))
    text += f"Стоимость крафта: 💦x{dicts[f'{index}']['disassemble'] * 2} Фрагментов оружия\n\n"
    for i in dicts:
        text += f"⭐" * index + f'💦x{dicts[f"{index + 1}"]["disassemble"] * 2}\n'
        weapons.append(("⭐" * index, f"{type}:{index + 1}:{dicts[f'{index + 1}']['disassemble'] * 2}"))
        index += 1
        if index == 6:
            break
    text += f"\n💦 У тебя: {ArmoryInv(callback.from_user.id).fragments} Фрагментов оружия "
    dialog_manager.dialog_data["text"] = text
    await dialog_manager.show()


@flags.throttling_key('games')
async def infocraft_weapon(callback: CallbackQuery, button: Button,
                           dialog_manager: DialogManager, item: str):
    with open(file='utils/weapons/weapon.json', mode='r', encoding="utf-8") as file:
        dicts = json.load(file, encoding="utf-8")[item]
    dicts = dicts
    weapon = dicts['1']
    text = f'{weapon["name"]}\n' \
           f'🔰 Прочность: {weapon["durability"]}/{weapon["max_durability"]}\n\n' \
           f'🔻мин. урон: {weapon["min_attack"]} \n' \
           f'🔺макс. урон: {weapon["max_attack"]}\n\n' \
           f'⚡️ Доп. шанс крита: {weapon["crit_chance"]}%\n' \
           f'🩸 Доп. множитель крит. урона: + {weapon["crit_multi"]}%\n\n' \
           f'--------------------\n'
    weapons = []
    index = 1
    weapons.append(('', f"{item}:{index}:{dicts[f'{index}']['disassemble'] * 2}"))
    text += f"Стоимость крафта: 💦x{dicts[f'{index}']['disassemble'] * 2} Фрагментов оружия\n\n"
    for i in dicts:
        text += f"⭐" * index + f'💦x{dicts[f"{index + 1}"]["disassemble"] * 2}\n'
        weapons.append(("⭐" * index, f"{item}:{index + 1}:{dicts[f'{index + 1}']['disassemble'] * 2}"))
        index += 1
        if index == 6:
            break

    text += f"\n💦 У тебя: {ArmoryInv(callback.from_user.id).fragments} Фрагментов оружия "
    dialog_manager.dialog_data["photo"] = armory_img[item]
    dialog_manager.dialog_data["weapons"] = weapons
    dialog_manager.dialog_data["text"] = text

    await dialog_manager.next()


CRAFT_MAIN_MENU_BUTTON = Start(
    text=Const("↩️"), id="back", state=states.Craft.MAIN,
)

scroll_craft_window = Window(
    DynamicMedia("photo"),
    Format("{info}"),
    ScrollingGroup(
        Select(
            Format("{item[0]}"),
            id="ms",
            items="products",
            item_id_getter=itemgetter(1),
            on_click=infocraft_weapon,
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
    state=states.Craft.MAIN,
    disable_web_page_preview=True
)
craft_info_window = Window(
    DynamicMedia("photo"),
    Format("{text}"),
    Column(
        Select(
            Format("🪡 Скарфтить {item[0]}"),  # E.g `✓ Apple (1/4)`
            id="s_weapons",
            item_id_getter=itemgetter(1),  # each item is a tuple with id on a first position
            items="weapons",  # we will use items from window data at a key `fruits`
            on_click=weapon_action
        )
    ),
    CRAFT_MAIN_MENU_BUTTON,
    getter=product_getter,
    state=states.Craft.INFO,
    disable_web_page_preview=True
)

craft_dialog = Dialog(
    scroll_craft_window,
    craft_info_window
)
