from aiogram import flags
from aiogram.enums import ContentType
from aiogram.types import CallbackQuery
from aiogram_dialog import Window, Dialog, DialogManager
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.kbd import Button, Row
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Format, Const

from config import armory_img
from handlers.users.bosses.armory.main import MAIN_MENU_BUTTON
from handlers.users.bosses.armory.states import ShopArmory
from utils.main.users import User
from utils.weapons.swords import ArmoryInv


def to_str3(money: int):
    b = f'{money:,}'
    return f"{b.replace(',', '.')}$"


async def product_getter(dialog_manager: DialogManager, **_kwargs):
    user = User(id=dialog_manager.event.from_user.id)
    image = MediaAttachment(
        ContentType.PHOTO, file_id=MediaId(armory_img['shop']))
    armory_inv = ArmoryInv(dialog_manager.event.from_user.id)
    return {
        "name": user.link,
        'image': image,
        'tokens': armory_inv.tokens,
    }


@flags.throttling_key('games')
async def on_click(callback: CallbackQuery, button: Button,
                   dialog_manager: DialogManager):
    if button.widget_id == 'None':
        return
    if button.widget_id.startswith("damage_"):
        armory_inv = ArmoryInv(callback.from_user.id)
        count = int(button.widget_id.split('_')[1])
        price = count * 7
        if price > armory_inv.tokens:
            return await callback.answer(f'Недостаточно 💠 tokens для покупки!', show_alert=True)
        armory_inv.editmany(tokens=armory_inv.tokens - price,
                            min_damage=armory_inv.min_damage + count,
                            max_damage=armory_inv.max_damage + count * 2)
        await callback.answer(f'Вы успешно купили ⬆️ +{count}/+{count * 2} к мин./макс. урону', show_alert=True)
    if button.widget_id.startswith("fragments_"):
        armory_inv = ArmoryInv(callback.from_user.id)
        count = int(button.widget_id.split('_')[1])
        price = count * 35
        if price > armory_inv.tokens:
            return await callback.answer(f'Недостаточно 💠 tokens для покупки!', show_alert=True)
        armory_inv.editmany(tokens=armory_inv.tokens - price,
                            fragments=armory_inv.fragments + count)
        await callback.answer(f'Вы успешно купили x{count}💦 Фрагментов оружия', show_alert=True)
    if button.widget_id.startswith("repair_"):
        armory_inv = ArmoryInv(callback.from_user.id)
        count = int(button.widget_id.split('_')[1])
        price = count * 5
        if price > armory_inv.tokens:
            return await callback.answer(f'Недостаточно 💠 tokens для покупки!', show_alert=True)
        armory_inv.editmany(tokens=armory_inv.tokens - price,
                            repair_kit=armory_inv.repair_kit + count)
        await callback.answer(f'Вы успешно купили x{count}⚒ Ремонтных комплектов', show_alert=True)
    await dialog_manager.show()


shop_armory_dialog = Dialog(
    Window(
        DynamicMedia("image"),
        Format('"{name}, 🏪 Товары 💠 магазина\n\n'
               '⬆️ +1/+2 к мин./макс. урону - 💠 7 tokens\n'
               '💦 Фрагмент оружия x1 - 💠 35 tokens\n'
               '⚒️ Ремонтный набор - 💠 5 tokens\n\n'
               '💠 У тебя: {tokens} tokens\n'),

        Row(
            Button(
                Const("⬆"),
                id=f'damage_1',
                on_click=on_click,
            ),
            Button(
                Const("⬆x5"),
                id=f'damage_5',
                on_click=on_click,
            ),
            Button(
                Const("⬆x50"),
                id=f'damage_50',
                on_click=on_click,
            ),
        ),

        Row(
            Button(
                Const("💦"),
                id=f'fragments_1',
                on_click=on_click,
            ),
            Button(
                Const("💦x5"),
                id=f'fragments_5',
                on_click=on_click,
            ),
            Button(
                Const("💦x50"),
                id=f'fragments_50',
                on_click=on_click,
            )
        ),

        Row(
            Button(
                Const("⚒️"),
                id=f'repair_1',
                on_click=on_click,
            ),
            Button(
                Const("⚒️x5"),
                id=f'repair_5',
                on_click=on_click,
            ),
            Button(
                Const(" "),
                id=f'None',
                on_click=on_click,
            ),
        ),

        MAIN_MENU_BUTTON,
        getter=product_getter,
        state=ShopArmory.MAIN,
        disable_web_page_preview=True
    )
)
