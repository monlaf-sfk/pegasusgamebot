from operator import itemgetter

from aiogram import flags, F
from aiogram.fsm.state import State, StatesGroup

from aiogram.types import Message, CallbackQuery

from aiogram_dialog import (
    Dialog, DialogManager,
    StartMode, Window,
)
from aiogram_dialog.widgets.kbd import (ScrollingGroup, Select, SwitchTo, Button, Row, CurrentPage, PrevPage, NextPage,
                                        Checkbox
                                        )
from aiogram_dialog.widgets.text import Format, Const

from config import bot_name
from handlers.users.clan.clan_rob import name_robs
from utils.clan.clan import Clanuser
from utils.clan.clan_rob import ClanRob
from utils.items.items import ItemsRob, items_rob
from utils.main.cash import to_str4
from utils.main.db import sql

from utils.main.users import User


class Shop(StatesGroup):
    LIST_PAGER = State()
    INFO_PAGER = State()


MAIN_MENU_BTN = SwitchTo(Const("Назад"), id="main", state=Shop.LIST_PAGER)


def to_str3(money: int):
    b = f'{money:,}'
    return f"{b.replace(',', '.')}$"


async def product_getter(dialog_manager: DialogManager, **_kwargs):
    user = User(id=dialog_manager.event.from_user.id)
    clan_id = dialog_manager.start_data.get("clan_id", None)
    clanrob = sql.execute(f"SELECT index_rob , plan_rob FROM ClanRob WHERE clan_id={clan_id}", fetch=True)[0]
    text = get_list_itemsforbuy(clanrob['index_rob'], clanrob['plan_rob'], user.id)

    return {
        "name": user.link,
        'text': text,
        "items": [(f'{index}. {item["name"]}{item["emoji"]} - {to_str3(item["sell_price"])}', index) for index, item
                  in enumerate(sql.get_all_data('items_rob'), start=1)],
    }


async def on_click(callback: CallbackQuery, button: Button,
                   dialog_manager: DialogManager, item_id: str):
    try:
        clanuser = Clanuser(user_id=callback.from_user.id)
    except:
        return await callback.answer(f'❌ У вас нет клана :(', show_alert=True,
                                     cache_time=1)
    try:
        clan_rob = ClanRob(clan_id=clanuser.clan_id)
    except:
        return await callback.answer(f'❗ покупка предметов доступна '
                                     f'только во время '
                                     f'ограбления 👍🏻')
    if not clan_rob.prepare and clan_rob.time_rob:
        return await callback.answer(f'❗  покупка предметов доступна '
                                     f'только во время подготовки к ограблению 👍🏻')
    if clan_rob.prepare and clan_rob.plan_rob == 0:
        return await callback.answer(f'❗ покупка предметов доступна только '
                                     f'после выбора плана ограбления 😩')

    items = ItemsRob(item_id)
    user = User(user=callback.from_user)
    if user.balance < items.sell_price:
        return await callback.answer(f'💲 Недостаточно средств на руках, нужно: {to_str4(items.sell_price)}',
                                     show_alert=True)
    count = items.get_item_count(user.id)
    if count and count >= 1:
        return await callback.answer(f'❌  У вас уже есть данный предмет', show_alert=True)
    items.set_item_count(user.id, 1)
    user.edit('balance', user.balance - items.sell_price)

    await callback.answer(f'💲 Вы купили {items.name} (x1) за {to_str4(items.sell_price)}', show_alert=True)
    if ItemsRob.check_allitems(user.id, name_robs[clan_rob.index_rob]['plan'][clan_rob.plan_rob]['subjects']):
        await callback.message.edit_text(f"{user.link}, все требуемые предметы куплены! 😯\n"
                                         "✅ Вы допущены к ограблению, ожидайте конца подготовки.",
                                         disable_web_page_preview=True)
        clanuser.edit('rob_involved', True)
        return await dialog_manager.done()
    await dialog_manager.show()


shop_dialog = Dialog(
    Window(
        Format("{name}, требуемые предметы для участия в ограблении:\n"
               '\n{text}\n'
               '▶️ Для покупки нажмите на кнопки или «Шоп [номер]»'),
        ScrollingGroup(

            Select(
                Format("{item[0]}"),
                id="cl",
                items="items",
                item_id_getter=itemgetter(1),
                on_click=on_click,
            ),
            width=2,
            height=7,
            hide_pager=True,
            id="scroll_with_pager",
        ),
        # Row(
        #     CurrentPage(scroll="scroll_with_pager", text=Format("{current_page1}/{pages}")),
        #     PrevPage(
        #         scroll='scroll_with_pager', text=Format("◀️"),
        #         when=F["current_page1"] != 1
        #     ),
        #     NextPage(
        #         scroll='scroll_with_pager', text=Format("▶️"),
        #         when=F["pages"] != F["current_page1"]
        #     )
        # ),
        getter=product_getter,
        state=Shop.LIST_PAGER,
        disable_web_page_preview=True
    )
)


def get_list_itemsforbuy(index_rob, plan_rob, user_id):
    numbers_emoji = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']
    text = ''
    for item_id in name_robs[index_rob]['plan'][plan_rob]['subjects']:
        emoji = ''.join(numbers_emoji[int(i)] for i in str(item_id))
        item = items_rob[item_id]
        if ItemsRob.check_item(user_id, item_id):
            text += f'{emoji} {item["emoji"]} {item["name"]} ✔\n'
        else:
            text += f'{emoji} {item["emoji"]} {item["name"]}\n'
    return text


@flags.throttling_key('default')
async def shop_list_handler(message: Message, dialog_manager: DialogManager):
    user = User(id=message.from_user.id)
    try:
        clanuser = Clanuser(user_id=message.from_user.id)
    except:
        return await message.reply(f'❗ {user.link}, этот раздел магазина доступен только игрокам, состоящим в клане ☹\n'
                                   '▶️ Введи «Кланы» чтобы посмотреть список всех кланов!',
                                   disable_web_page_preview=True)
    try:
        clan_rob = ClanRob(clan_id=clanuser.clan_id)
    except:
        return await message.reply(f'❗ {user.link}, покупка предметов доступна '
                                   f'только во время '
                                   f'ограбления 👍🏻',
                                   disable_web_page_preview=True)
    if not clan_rob.prepare and clan_rob.time_rob:
        return await message.reply(f'❗ {user.link}, покупка предметов доступна '
                                   f'только во время подготовки к ограблению 👍🏻',
                                   disable_web_page_preview=True)
    if clan_rob.prepare and clan_rob.plan_rob == 0:
        return await message.reply(f'❗ {user.link}, покупка предметов доступна только '
                                   f'после выбора плана ограбления 😩',
                                   disable_web_page_preview=True)
    arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[
        0].lower() else message.text.split()[2:]
    if message.chat.id == message.from_user.id and len(arg) == 0:
        await dialog_manager.start(Shop.LIST_PAGER, mode=StartMode.NEW_STACK, data={'clan_id': clanuser.clan_id})
    else:
        if len(arg) == 0:
            text = get_list_itemsforbuy(clan_rob.index_rob, clan_rob.plan_rob, user.id)
            return await message.reply(f'{user.link}, требуемые предметы для участия в ограблении: \n{text}\n'
                                       f'✅ Для покупки введите «Шоп [номер]»',
                                       disable_web_page_preview=True)

        if len(arg) >= 1 and arg[0].isdigit():
            try:
                item_id = int(arg[0])
                items = ItemsRob(item_id)
            except:
                text = get_list_itemsforbuy(clan_rob.index_rob, clan_rob.plan_rob, user.id)
                return await message.reply(f'{user.link}, требуемые предметы для участия в ограблении: \n{text}\n'
                                           f'✅ Для покупки введите «Шоп [номер]»',
                                           disable_web_page_preview=True)

            if user.balance < items.sell_price:
                return await message.reply(
                    f'💲 {user.link}, Недостаточно средств на руках, нужно: {to_str4(items.sell_price)}',
                    disable_web_page_preview=True)
            count = items.get_item_count(user.id)
            if count and count >= 1:
                return await message.reply(f'❌ {user.link}, У вас уже есть данный предмет',
                                           disable_web_page_preview=True)
            items.set_item_count(user.id, 1)
            user.edit('balance', user.balance - items.sell_price)

            await message.reply(f'💲 {user.link}, Вы купили {items.name} (x1) за {to_str4(items.sell_price)}',
                                disable_web_page_preview=True)
            if ItemsRob.check_allitems(user.id, name_robs[clan_rob.index_rob]['plan'][clan_rob.plan_rob]['subjects']):
                await message.reply(f"{user.link}, все требуемые предметы куплены! 😯\n"
                                    "✅ Вы допущены к ограблению, ожидайте конца подготовки.",
                                    disable_web_page_preview=True)
                clanuser.edit('rob_involved', True)
