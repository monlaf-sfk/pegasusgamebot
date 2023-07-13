from datetime import datetime
from operator import itemgetter

from aiogram import flags, F
from aiogram.fsm.state import State, StatesGroup

from aiogram.types import Message, CallbackQuery

from aiogram_dialog import (
    Dialog, DialogManager,
    StartMode, Window,
)
from aiogram_dialog.widgets.kbd import (ScrollingGroup, Select, SwitchTo, Button, Row, CurrentPage, PrevPage, NextPage
                                        )
from aiogram_dialog.widgets.text import Format, Const

from utils.clan.clan import Clan
from utils.main.db import sql
from utils.main.users import User


class DialogSG(StatesGroup):
    DEFAULT_PAGER = State()
    INFO_PAGER = State()


MAIN_MENU_BTN = SwitchTo(Const("Назад"), id="main", state=DialogSG.DEFAULT_PAGER)


async def product_getter(dialog_manager: DialogManager, **_kwargs):
    user = User(id=dialog_manager.event.from_user.id)
    text = dialog_manager.dialog_data.get("text", None)
    return {
        "name": user.link,
        "count_clans": len(sql.get_all_data('clans')),
        'text': text,
        "clans": [(f"🛡️ {i[1]} | 🆔 {i[0]} | {'🔒' if i[8] == 1 else '🚪' if i[8] == 0 else '📝'}", i[0]) for i in
                  sql.get_all_data('clans')],
    }


async def on_click(callback: CallbackQuery, button: Button,
                   dialog_manager: DialogManager, item_id: str):
    clan = Clan(clan_id=int(item_id))
    lol = datetime.now() - clan.reg_date
    xd = f'{lol.days} дн.' if lol.days > 0 else f'{int(lol.total_seconds() // 3600)} час.' \
        if lol.total_seconds() > 59 else f'{int(lol.seconds)} сек.'

    text = f'Информация о клане:\n' \
           f'✏️ Название: {clan.name}' \
           f'\n' f'🛡 Уровень: {clan.level}\n' \
           f'🔎 ID клана: {clan.id}\n' \
           f'🔒 Тип: {"Закрыт" if clan.type == 1 else "Открыт" if clan.type == 0 else "По Приглашению"}\n' \
           f'♨ Префикс: {clan.prefix if clan.prefix != "" else "Нету"}\n' \
           f'➖➖➖➖➖➖➖➖\n' \
           f'🏆 Рейтинг: {clan.rating}\n' \
           f'📋 Описание: {clan.description}\n\n' \
           f'➖➖➖➖➖➖➖➖➖\n' \
           f''f' 👥 Участники ({clan.members}/50)\n' \
           f'📅 Дата: {clan.reg_date}:({xd})'
    dialog_manager.dialog_data["text"] = text if clan.type != 1 else 'Информация засекречена!'
    await dialog_manager.next()


clan_dialog = Dialog(
    Window(
        Format("{name} Инфорсация о кланах\n"
               "➖➖➖➖➖➖➖➖\n"
               "🚪 - Открыт | 📝 - Вход по заявкам | 🔒 - Закрыт\n"
               "➖➖➖➖➖➖➖➖\n"
               "Список кланов ({count_clans}шт.): \n"),
        ScrollingGroup(

            Select(
                Format("{item[0]}"),
                id="cl",
                items="clans",
                item_id_getter=itemgetter(1),
                on_click=on_click,
            ),
            width=1,
            height=5,
            hide_pager=True,
            id="scroll_with_pager",
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
            )
        ),
        getter=product_getter,
        state=DialogSG.DEFAULT_PAGER,
        disable_web_page_preview=True
    ),
    Window(
        Format("{name} {text}"),
        MAIN_MENU_BTN,
        getter=product_getter,
        state=DialogSG.INFO_PAGER,
        disable_web_page_preview=True

    )
)


@flags.throttling_key('default')
async def clan_list_handler(message: Message, dialog_manager: DialogManager):
    # it is important to reset stack because user wants to restart everything

    await dialog_manager.start(DialogSG.DEFAULT_PAGER, mode=StartMode.NEW_STACK)
