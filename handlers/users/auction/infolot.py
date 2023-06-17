import time

from aiogram import flags
from aiogram.enums import ContentType
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, Dialog, Window, StartMode
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format

from filters.users import flood_handler
from handlers.users.auction import states
from loader import bot
from utils.auction import Auction
from utils.main.cash import to_str4
from utils.main.db import sql, timetostr
from utils.main.users import User


async def product_getter(dialog_manager: DialogManager, **_kwargs):
    return {
        'text': dialog_manager.start_data.get("text"),
        'uuid': dialog_manager.start_data.get("uuid"),
        'price': to_str4(dialog_manager.start_data.get("price", 1)),
    }


@flags.throttling_key('games')
async def update_lot(callback: CallbackQuery, button: Button,
                     dialog_manager: DialogManager):
    item_id = dialog_manager.start_data.get("uuid")
    price_callback = dialog_manager.start_data.get("price")
    try:
        auction = Auction(str(item_id))
    except:
        await callback.answer('⚠️ Это уже не актуальный лот!', show_alert=True)
        return await dialog_manager.done()
    user = User(id=callback.from_user.id)
    price_curs = sql.execute("SELECT coin_kurs FROM other", commit=False, fetch=True)[0][0]
    price = auction.price + ((price_curs * auction.count) / 10)
    if button.widget_id == 'stavka':
        if price > int(price_callback):
            return await callback.answer('❌ Это не актуальная цена !\n'
                                         '🔄 Обновите страницу', show_alert=True)
        if price > user.balance:
            return await callback.answer('❌ Недостаточно средств для ставки!\n'
                                         f'Требуется: {price}', show_alert=True)
        if auction.seller == user.id:
            return await callback.answer('❌ Свои лоты нельзя покупать!', show_alert=True)
        if auction.costumers == user.id:
            return await callback.answer('❌ Это и так ваша ставка!', show_alert=True)
        user.edit('balance', user.balance - price)
        if auction.costumers:
            user_costumers = User(id=auction.costumers)
            user_costumers.edit('balance', user_costumers.balance + auction.price)
            await bot.send_message(chat_id=auction.costumers,
                                   text=f'Вашу ставку перебили ID: <code>{auction.uuid4}</code>\n'
                                        f'👁‍🗨 /lot_{auction.uuid4}', disable_web_page_preview=True)

        if int(time.time()) - auction.time > 840:
            auction.editmany(price=price, costumers=user.id,
                             time=auction.time + 60)
        else:
            auction.editmany(price=price, costumers=user.id)
        await callback.answer(f'✅ Вы успешно cделали ставку на {auction.uuid4} за {to_str4(price)}$',
                              disable_web_page_preview=True, show_alert=True)

    text = f'❓ Информация о лоте:\n' \
           f'🆔: <code>{auction.uuid4}</code>\n' \
           f'🔄 Количество коинов: x{to_str4(auction.count)} 🪙\n' \
           f'➖➖➖➖➖➖➖➖\n' \
           f'💲 Текущая ставка: {to_str4(auction.price)} {"<i>(Твоя ставка)</i>" if auction.costumers == callback.from_user.id else ""}\n' \
           f'🕐 Окончание через: {timetostr(auction.time + 900 - int(time.time()))}' \
           f'👁‍🗨 /lot_{auction.uuid4}'
    dialog_manager.start_data["text"] = text
    dialog_manager.start_data["price"] = price
    await dialog_manager.show()


@flags.throttling_key('games')
async def auction_lotinfo_handler(message: Message, dialog_manager: DialogManager):
    flood = await flood_handler(message)
    if flood:
        arg = message.text.split('_')[1:]
        arg = str(arg[0][:15])
        if arg == '':
            return await message.reply('❌ Используйте:\n'
                                       '<code>/lot_(id) </code>')
        try:
            auction = Auction(arg)
        except:
            return await message.reply('❌ Неверный id предмета!')
        text = f'❓ Информация о лоте:\n' \
               f'🆔: <code>{auction.uuid4}</code>\n' \
               f'🔄 Количество коинов: x{to_str4(auction.count)} 🪙\n' \
               f'➖➖➖➖➖➖➖➖\n' \
               f'💲 Текущая ставка: {to_str4(auction.price)} {"<i>(Твоя ставка)</i>" if auction.costumers == message.from_user.id else ""}\n' \
               f'🕐 Окончание через: {timetostr(auction.time + 900 - int(time.time()))}' \
               f'👁‍🗨 /lot_{auction.uuid4}'
        price_curs = sql.execute("SELECT coin_kurs FROM other", commit=False, fetch=True)[0][0]
        price = auction.price + ((price_curs * auction.count) / 10)
        await dialog_manager.start(states.InfoLot.MAIN, mode=StartMode.NEW_STACK,
                                   data={'uuid': arg, 'price': price, 'text': text})


infolot_window = Dialog(
    Window(
        Format("{text}"),
        StaticMedia(
            path="assets/img/diologs/auction_main.png",
            type=ContentType.PHOTO),
        Button(
            Format("Сделать ставку • {price}💲"),
            id=f'stavka',
            on_click=update_lot,
        ),
        Button(
            Const("🔄 Обновить"),
            id=f'update',
            on_click=update_lot
        ),
        getter=product_getter,
        state=states.InfoLot.MAIN,
    )
)
