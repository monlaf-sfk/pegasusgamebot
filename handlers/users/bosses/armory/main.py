from aiogram import flags
from aiogram.enums import ContentType
from aiogram.types import Message
from aiogram_dialog import (
    Dialog, Window, LaunchMode, DialogManager, StartMode,
)
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.kbd import (
    Start, Row,
)
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Const, Format

from config import armory_img
from handlers.users.bosses.armory import states
from utils.main.db import sql
from utils.weapons.swords import ArmoryInv, Armory


async def product_getter(dialog_manager: DialogManager, **_kwargs):
    armory_inv = ArmoryInv(dialog_manager.event.from_user.id)
    image = MediaAttachment(
        ContentType.PHOTO, file_id=MediaId(armory_img['armory_menu'])
    )
    uniq_id = sql.execute("SELECT uniq_id FROM armory WHERE armed=True", fetchone=True)
    if uniq_id:
        armory = Armory(uniq_id)
        damage = armory.weapon['min_attack'] + armory.weapon['max_attack']
    else:
        damage = 0
    return {
        'tokens': armory_inv.tokens,
        'fragmets': armory_inv.fragments,
        'repair_kit': armory_inv.repair_kit,
        'min_damage': armory_inv.min_damage,
        'max_damage': armory_inv.max_damage,
        'photo': image,
        'bm': armory_inv.min_damage + armory_inv.max_damage + damage
    }


main_armory_dialog = Dialog(
    Window(
        DynamicMedia("photo"),
        Format("""
💪 БМ: {bm}
------------------
🗡️ Базовый урон:
    🔻мин. урон: {min_damage}
    🔺макс. урон: {max_damage}
------------------
🎒 Инвентарь:
💠x{tokens} 💦x{fragmets}  ⚒️x{repair_kit}
"""),
        Start(
            text=Const("⚔ Мой арсенал"),
            id="arsenal",
            state=states.Arsenal.MAIN,
        ),
        Row(
            Start(
                text=Const("🪡 Крафт"),
                id="craft",
                state=states.Craft.MAIN,
            ),
            Start(
                text=Const("💦 Разбор оружия"),
                id="dissamble",
                state=states.Parsing.MAIN,
            )
        ),
        Row(
            # Start(
            # text=Const("🏵 Пробуждение"),
            # id="cal",
            # state=states.Awakening.MAIN
            # ),
            Start(
                text=Const("💫 Улучшение"),
                id="upgrade",
                state=states.Improvement.MAIN,
            ),

        ),
        Start(
            text=Const("🏪 Магазин"),
            id="shop",
            state=states.ShopArmory.MAIN,
        ),
        state=states.Armory.MAIN,
        getter=product_getter,
    ),
    launch_mode=LaunchMode.ROOT,
)

MAIN_MENU_BUTTON = Start(
    text=Const("↩️"),
    id="__main__",
    state=states.Armory.MAIN,
)


@flags.throttling_key('games')
async def start_armory(message: Message, dialog_manager: DialogManager):
    # it is important to reset stack because user wants to restart everything
    await dialog_manager.start(states.Armory.MAIN, mode=StartMode.NEW_STACK)
