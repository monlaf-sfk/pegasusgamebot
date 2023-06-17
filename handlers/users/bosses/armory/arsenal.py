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

from . import states
from .main import MAIN_MENU_BUTTON


async def product_getter(dialog_manager: DialogManager, **_kwargs):
    user = User(id=dialog_manager.event.from_user.id)

    image = MediaAttachment(
        ContentType.PHOTO, file_id=MediaId(dialog_manager.dialog_data.get("photo", armory_img['armory_menu']))
    )

    list = [(f"{Armory.get_json(i[3], i[2])['name'] + ' ✅' if i[5] else Armory.get_json(i[3], i[2])['name']}",
             f"{i[0]}") for i in
            sql.execute(f"SELECT * FROM armory WHERE user_id={user.id} ORDER BY weapon_id DESC", fetch=True)]
    text = dialog_manager.dialog_data.get("text", None)
    if len(list) == 0:
        return {
            'info': f"❓ {user.link}, Нету оружий",
            'text': text,
            "products": list,
            'uniqid': None,
            'notnone': False,
            'photo': image,
            'armed': dialog_manager.dialog_data.get("armed", False)
        }
    return {
        'info': f"❓ {user.link}, Вот все доступные",
        'text': text,
        "products": list,
        'uniqid': None,
        'notnone': True,
        'photo': image,
        'armed': dialog_manager.dialog_data.get("armed", False)

    }


@flags.throttling_key('games')
async def weapon_action(callback: CallbackQuery, button: Button,
                        dialog_manager: DialogManager):
    uniqid = dialog_manager.dialog_data.get("uniqid")
    try:
        armory = Armory(uniq_id=uniqid)
    except:
        await callback.answer('🔰 Даное оружие больше недоступно!\n', show_alert=True)
        return await dialog_manager.done()

    durability = armory.durability
    armed = armory.armed

    if button.widget_id == 'restore':
        if armory.durability < armory.weapon["max_durability"]:
            armory_inv = ArmoryInv(user_id=callback.from_user.id)
            if armory_inv.repair_kit >= 1:
                armory_inv.edit('repair_kit', armory_inv.repair_kit - 1)
                durability = armory.edit('durability', armory.weapon["max_durability"])
                await callback.answer('🔰 Прочность восстановлена!\n', show_alert=True)
            else:
                await callback.answer('⚒ У вас нехватает ремонтных комплектов!\n', show_alert=True)
        else:
            await callback.answer('🔰 У вас прочность на максимуме!\n', show_alert=True)
    elif button.widget_id == 'takeoff':
        armed = armory.edit('armed', False)
    elif button.widget_id == 'takeon':
        try:
            armory2 = Armory(armed=True, user_id=callback.from_user.id)
        except:
            armory2 = None
        if armory2 is None:
            armed = armory.edit('armed', True)
        else:
            await callback.answer('🔰 У вас уже есть надетое оружие \n', show_alert=True)
    elif button.widget_id == 'synthes':
        count = sql.execute(
            f"SELECT * FROM armory WHERE user_id={callback.from_user.id} AND weapon_id={armory.weapon_id} AND type ='{armory.type}' AND uniq_id!={uniqid} AND armed=False",
            fetch=True)
        if count != None and len(count) >= 1:
            if armory.weapon_id + 1 <= 6:
                Armory.delete(count[0][0])
                armory.edit('weapon_id', armory.weapon_id + 1)
                await callback.answer('🧬 Успешно синтезировал', show_alert=True)
                dialog_manager.dialog_data["photo"] = armory_img['armory_menu']
                return await dialog_manager.back()
            else:
                await callback.answer('❌ Синтез невозможен', show_alert=True)
        else:
            await callback.answer('🧬 Нужно два одинаковых оружия!', show_alert=True)

    text = f'{armory.weapon["name"]}\n' \
           f'🔰 Прочность: {durability}/{armory.weapon["max_durability"]}\n\n' \
           f'🔻мин. урон: {armory.weapon["min_attack"]} \n' \
           f'🔺макс. урон: {armory.weapon["max_attack"]}\n\n' \
           f'⚡️ Доп. шанс крита: {armory.weapon["crit_chance"]}%\n' \
           f'🩸 Доп. множитель крит. урона: + {armory.weapon["crit_multi"]}%\n'

    dialog_manager.dialog_data["text"] = text
    dialog_manager.dialog_data["armed"] = armed
    dialog_manager.dialog_data["uniqid"] = uniqid
    dialog_manager.dialog_data["photo"] = armory.image
    await dialog_manager.show()


@flags.throttling_key('games')
async def info_weapon(callback: CallbackQuery, button: Button,
                      dialog_manager: DialogManager, item: str):
    uniqid = item
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
    dialog_manager.dialog_data["photo"] = armory.image
    await dialog_manager.next()


ARSENAL_MAIN_MENU_BUTTON = Start(
    text=Const("↩️"), id="back", state=states.Arsenal.MAIN,
)

scroll_arsenal_window = Window(
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
    state=states.Arsenal.MAIN,
    disable_web_page_preview=True
)
arsenal_info_window = Window(

    DynamicMedia("photo"),
    Format("{text}"),
    Button(
        Const("🛠 Воcстоновить прочность"),
        id=f'restore',
        on_click=weapon_action,
        when=F['armed'] == True
    ),
    Button(
        Const("🗡 Экипировать"),
        id=f'takeon',
        on_click=weapon_action,
        when=F['armed'] == False
    ),
    Button(
        Const("⬇ Снять"),
        id=f'takeoff',
        on_click=weapon_action,
        when=F['armed'] == True
    ),
    Button(
        Const("🧬 Синтезироввать"),
        id=f'synthes',
        on_click=weapon_action,
        when=F['armed'] == False
    ),
    ARSENAL_MAIN_MENU_BUTTON,
    getter=product_getter,
    state=states.Arsenal.INFO,
    disable_web_page_preview=True
)

arsenal_dialog = Dialog(
    scroll_arsenal_window,
    arsenal_info_window
)
