from operator import itemgetter

import numpy as np
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
from handlers.users.bosses.armory import states
from handlers.users.bosses.armory.main import MAIN_MENU_BUTTON
from utils.main.db import sql
from utils.main.users import User
from utils.weapons.swords import Armory, ArmoryInv
from utils.weapons.weapon import weapons_item


async def product_getter(dialog_manager: DialogManager, **_kwargs):
    user = User(id=dialog_manager.event.from_user.id)
    list = [(f"{weapons_item[i[3]][i[2]]['name']}",
             f"{i[0]}:{i[2]}:{i[3]}") for i in
            sql.execute(f"SELECT * FROM armory WHERE user_id={user.id} ORDER BY weapon_id DESC", fetch=True) if
            i[2] > 5 and i[5] == False]
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
            'photo': image,
            'armed': dialog_manager.dialog_data.get("armed", False),
        }
    return {
        'info': f"❓ {user.link}, Вот все доступные",
        'text': text,
        "products": list,
        'uniqid': None,
        'notnone': True,
        'photo': image,
        'armed': dialog_manager.dialog_data.get("armed", False),

    }


@flags.throttling_key('games')
async def disassemble_action(callback: CallbackQuery, button: Button,
                             dialog_manager: DialogManager):
    uniqid = dialog_manager.dialog_data["uniqid"]
    try:
        armory = Armory(uniq_id=uniqid)
    except:
        await callback.answer('🔰 Даное оружие больше недоступно!\n', show_alert=True)
        return await dialog_manager.done()

    if armory.weapon_id >= 6 and armory.weapon_id != 16:
        armory_inv = ArmoryInv(user_id=callback.from_user.id)
        if button.widget_id == 'improve':
            if armory_inv.fragments >= armory.weapon["upgrade_cost"]:
                chance = np.random.choice([1, 2], 1,
                                          p=[1 - armory.weapon["upgrade_chance"], armory.weapon["upgrade_chance"]])[0]
                armory_inv.edit('fragments', armory_inv.fragments - armory.weapon["upgrade_cost"])
                if chance == 2:
                    armory.editmany(weapon_id=armory.weapon_id + 1,
                                    durability=armory.weapon['max_durability'])
                    await callback.answer('Успех!\n'
                                          f'🗡 Получено оружие {armory.weapon["name"]}',
                                          show_alert=True)
                    dialog_manager.dialog_data["photo"] = armory_img['armory_menu']
                else:
                    await callback.answer('❌ Провал! Твое оружие осталось прежним',
                                          show_alert=True)
            else:
                await callback.answer('❌ Недостаточно Фрагментов оружия!',
                                      show_alert=True)
        elif button.widget_id == 'improve100':
            if armory_inv.fragments >= armory.weapon["upgrade_cost"] * 2:
                armory_inv.edit('fragments', armory_inv.fragments - armory.weapon["upgrade_cost"] * 2)
                armory.editmany(weapon_id=armory.weapon_id + 1,
                                durability=armory.weapon['max_durability'])
                await callback.answer('Успех!\n'
                                      f'🗡 Получено оружие {armory.weapon["name"]}',
                                      show_alert=True)
                dialog_manager.dialog_data["photo"] = armory_img['armory_menu']
            else:
                await callback.answer('❌ Недостаточно Фрагментов оружия!',
                                      show_alert=True)
    else:
        await callback.answer('❌ Улучшение невозможно', show_alert=True)
    dialog_manager.dialog_data["photo"] = armory.image
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
           f'🩸 Доп. множитель крит. урона: + {armory.weapon["crit_multi"]}%\n\n'
    text += f"Стоимость улучшения: 💦 {armory.weapon['upgrade_cost']}\n" \
            f"Вероятность улучшения: {round(armory.weapon['upgrade_chance'] * 100)}%\n\n" \
            f"Стоимость 100% улучшения: 💦{armory.weapon['upgrade_cost'] * 2}\n"
    text += f"\n💦 У тебя: {ArmoryInv(callback.from_user.id).fragments} Фрагментов оружия "
    dialog_manager.dialog_data["text"] = text
    dialog_manager.dialog_data["armed"] = armory.armed
    dialog_manager.dialog_data["uniqid"] = uniqid

    dialog_manager.dialog_data["photo"] = armory.image
    await dialog_manager.next()


IMPROV_MAIN_MENU_BUTTON = Start(
    text=Const("↩️"), id="back", state=states.Improvement.MAIN,
)
scroll_improv_armory_window = Window(
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
    state=states.Improvement.MAIN,
    disable_web_page_preview=True
)
improving_info_window = Window(
    DynamicMedia("photo"),
    Format("{text}"),
    Button(
        Const("💫 Улучшить"),
        id=f'improve',
        on_click=disassemble_action,
        when='notnone'
    ),
    Button(
        Const("💫 100% Улучшить"),
        id=f'improve100',
        on_click=disassemble_action,
        when='notnone'
    ),
    IMPROV_MAIN_MENU_BUTTON,
    getter=product_getter,
    state=states.Improvement.INFO,
    disable_web_page_preview=True
)

improvement_armory_dialog = Dialog(
    scroll_improv_armory_window,
    improving_info_window
)
