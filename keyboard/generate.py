from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

buy_ferm_kb = InlineKeyboardBuilder()
buy_ferm_kb.add(InlineKeyboardButton(text='🛒 Купить ферму', switch_inline_query_current_chat='Ферма купить '))

bitcoin_kb = InlineKeyboardBuilder()
bitcoin_kb.add(InlineKeyboardButton(text='Вывести 💸', switch_inline_query_current_chat='Ферма снять'))
bitcoin_kb.add(InlineKeyboardButton(text='Продать 🗑️', switch_inline_query_current_chat='Ферма продать'))
bitcoin_kb.add(InlineKeyboardButton(text='Налоги 💲', switch_inline_query_current_chat='Ферма налог'))
bitcoin_kb.add(
    InlineKeyboardButton(text='Купить видеокарты 📼', switch_inline_query_current_chat='Видеокарты купить 1'))
bitcoin_kb.adjust(2)
show_balance_kb = InlineKeyboardBuilder()
show_balance_kb.add(InlineKeyboardButton(text='💰 Баланс', switch_inline_query_current_chat='Баланс'))

show_ferm_kb = InlineKeyboardBuilder()
show_ferm_kb.add(InlineKeyboardButton(text='🖥️ Моя ферма', switch_inline_query_current_chat='Ферма'))

buy_business_kb = InlineKeyboardBuilder()
buy_business_kb.add(InlineKeyboardButton(text='🛒 Купить биз', switch_inline_query_current_chat='Биз купить '))

show_business_kb = InlineKeyboardBuilder()
show_business_kb.add(InlineKeyboardButton(text='🧑🏿‍💼 Мой бизнес', switch_inline_query_current_chat='Биз'))

business_kb = InlineKeyboardBuilder()
business_kb.add(InlineKeyboardButton(text='Снять 💸', switch_inline_query_current_chat='Биз снять'))
business_kb.add(InlineKeyboardButton(text='Налог 💲', switch_inline_query_current_chat='Биз налог'))
business_kb.add(InlineKeyboardButton(text='Продать 💰', switch_inline_query_current_chat='Биз продать'))
business_kb.add(InlineKeyboardButton(text='Открыть 🟢', switch_inline_query_current_chat='Биз открыть'))
business_kb.adjust(2)

show_inv_kb = InlineKeyboardBuilder()
show_inv_kb.add(InlineKeyboardButton(text='🎒 Мой инвентарь', switch_inline_query_current_chat='Инв'))

buy_airplane_kb = InlineKeyboardBuilder()
buy_airplane_kb.add(InlineKeyboardButton(text='🛒 Купить самолёт', switch_inline_query_current_chat='Самолёт купить'))

airplane_kb = InlineKeyboardBuilder()
airplane_kb.add(InlineKeyboardButton(text='Вывести 💸', switch_inline_query_current_chat='Самолёт снять'))
airplane_kb.add(InlineKeyboardButton(text='Продать 🗑️', switch_inline_query_current_chat='Самолёт продать'))
airplane_kb.add(InlineKeyboardButton(text='Налоги 💲', switch_inline_query_current_chat='Самолёт оплатить'))
airplane_kb.add(InlineKeyboardButton(text='Лететь ✈️', switch_inline_query_current_chat='Самолёт лететь'))
airplane_kb.adjust(2)

show_airplane_kb = InlineKeyboardBuilder()
show_airplane_kb.add(InlineKeyboardButton(text='✈️ Мой самолёт', switch_inline_query_current_chat='Самолёт'))

buy_car_kb = InlineKeyboardBuilder()
buy_car_kb.add(InlineKeyboardButton(text='🛒 Купить машину', switch_inline_query_current_chat='Машина купить'))

car_kb = InlineKeyboardBuilder()
car_kb.add(InlineKeyboardButton(text='Вывести 💸', switch_inline_query_current_chat='Машина снять'))
car_kb.add(InlineKeyboardButton(text='Продать 🗑️', switch_inline_query_current_chat='Машина продать'))
car_kb.add(InlineKeyboardButton(text='Налоги 💲', switch_inline_query_current_chat='Машина оплатить'))
car_kb.add(InlineKeyboardButton(text='Ехать 🛻', switch_inline_query_current_chat='Машина ехать'))
car_kb.adjust(2)

show_car_kb = InlineKeyboardBuilder()
show_car_kb.add(InlineKeyboardButton(text='🛻 Моя машина', switch_inline_query_current_chat='Машина'))

buy_moto_kb = InlineKeyboardBuilder()
buy_moto_kb.add(InlineKeyboardButton(text='🛒 Купить мото', switch_inline_query_current_chat='Мото купить'))

moto_kb = InlineKeyboardBuilder()
moto_kb.add(InlineKeyboardButton(text='Вывести 💸', switch_inline_query_current_chat='Мото снять'))
moto_kb.add(InlineKeyboardButton(text='Продать 🗑️', switch_inline_query_current_chat='Мото продать'))
moto_kb.add(InlineKeyboardButton(text='Налоги 💲', switch_inline_query_current_chat='Мото оплатить'))
moto_kb.add(InlineKeyboardButton(text='Ехать 🏍️', switch_inline_query_current_chat='Мото ехать'))
moto_kb.adjust(2)

show_moto_kb = InlineKeyboardBuilder()
show_moto_kb.add(InlineKeyboardButton(text='🏍️ Мой мотоцикл', switch_inline_query_current_chat='Мото'))

buy_vertolet_kb = InlineKeyboardBuilder()
buy_vertolet_kb.add(InlineKeyboardButton(text='🛒 Купить вертолёт', switch_inline_query_current_chat='Вертолёт купить'))

vertolet_kb = InlineKeyboardBuilder()
vertolet_kb.add(InlineKeyboardButton(text='Вывести 💸', switch_inline_query_current_chat='Вертолёт снять'))
vertolet_kb.add(InlineKeyboardButton(text='Продать 🗑️', switch_inline_query_current_chat='Вертолёт продать'))
vertolet_kb.add(InlineKeyboardButton(text='Налоги 💲', switch_inline_query_current_chat='Вертолёт оплатить'))
vertolet_kb.add(InlineKeyboardButton(text='Лететь 🚁', switch_inline_query_current_chat='Вертолёт лететь'))
vertolet_kb.adjust(2)

show_vertolet_kb = InlineKeyboardBuilder()
show_vertolet_kb.add(InlineKeyboardButton(text='🚁 Мой вертолёт', switch_inline_query_current_chat='Вертолёт'))

buy_yaxta_kb = InlineKeyboardBuilder()
buy_yaxta_kb.add(InlineKeyboardButton(text='🛒 Купить яхту', switch_inline_query_current_chat='Яхта купить'))

yaxta_kb = InlineKeyboardBuilder()
yaxta_kb.add(InlineKeyboardButton(text='Вывести 💸', switch_inline_query_current_chat='Яхта снять'))
yaxta_kb.add(InlineKeyboardButton(text='Продать 🗑️', switch_inline_query_current_chat='Яхта продать'))
yaxta_kb.add(InlineKeyboardButton(text='Налоги 💲', switch_inline_query_current_chat='Яхта оплатить'))
yaxta_kb.add(InlineKeyboardButton(text='Плыть ⛵', switch_inline_query_current_chat='Яхта плыть'))
yaxta_kb.adjust(2)

show_yaxta_kb = InlineKeyboardBuilder()
show_yaxta_kb.add(InlineKeyboardButton(text='⛵ Моя яхта', switch_inline_query_current_chat='Яхта'))

buy_house_kb = InlineKeyboardBuilder()
buy_house_kb.add(InlineKeyboardButton(text='🛒 Купить дом', switch_inline_query_current_chat='Дом купить '))

show_house_kb = InlineKeyboardBuilder()
show_house_kb.add(InlineKeyboardButton(text='🏠 Мой дом', switch_inline_query_current_chat='Дом'))

house_kb = InlineKeyboardBuilder()
house_kb.add(InlineKeyboardButton(text='Снять 💸', switch_inline_query_current_chat='Дом снять'))
house_kb.add(InlineKeyboardButton(text='Налог 💲', switch_inline_query_current_chat='Дом налог'))
house_kb.add(InlineKeyboardButton(text='Продать 💰', switch_inline_query_current_chat='Дом продать'))
house_kb.add(InlineKeyboardButton(text='Аренда 🟢', switch_inline_query_current_chat='Дом аренда'))
house_kb.adjust(2)

buy_computer_kb = InlineKeyboardBuilder()
buy_computer_kb.add(
    InlineKeyboardButton(text='🛒 Купить Компьютер', switch_inline_query_current_chat='Компьютер купить '))

show_computer_kb = InlineKeyboardBuilder()
show_computer_kb.add(InlineKeyboardButton(text='💻 Мой Компьютер', switch_inline_query_current_chat='Компьютер'))


def computer_keyboard(id):
    computer_kb = InlineKeyboardBuilder()
    computer_kb.add(InlineKeyboardButton(text='Снять 💸', switch_inline_query_current_chat='Компьютер снять'))
    computer_kb.add(InlineKeyboardButton(text='Продать 💰', switch_inline_query_current_chat='Компьютер продать'))
    computer_kb.add(InlineKeyboardButton(text='🥷 Взломать', callback_data=f'computer_{id}'))
    return computer_kb.adjust(2).as_markup()


ride_car_kb = InlineKeyboardBuilder()
ride_car_kb.add(InlineKeyboardButton(text='🚗 Ехать ещё раз', switch_inline_query_current_chat='Машина ехать'))

ride_airplane_kb = InlineKeyboardBuilder()
ride_airplane_kb.add(InlineKeyboardButton(text='✈️ Лететь ещё раз', switch_inline_query_current_chat='Самолёт лететь'))

ride_moto_kb = InlineKeyboardBuilder()
ride_moto_kb.add(InlineKeyboardButton(text='🏍️ Ехать ещё раз', switch_inline_query_current_chat='Мото ехать'))

ride_yaxta_kb = InlineKeyboardBuilder()
ride_yaxta_kb.add(InlineKeyboardButton(text='⛵ Плыть ещё раз', switch_inline_query_current_chat='Яхта плыть'))

ride_vertolet_kb = InlineKeyboardBuilder()
ride_vertolet_kb.add(InlineKeyboardButton(text='🚁 Лететь ещё раз', switch_inline_query_current_chat='Вертолёт лететь'))

show_city_kb = InlineKeyboardBuilder()
show_city_kb.add(InlineKeyboardButton(text='🏙 Город', switch_inline_query_current_chat='Город'))

city_water_kb = InlineKeyboardBuilder()
city_water_kb.add(
    InlineKeyboardButton(text='💧 Построить еще', switch_inline_query_current_chat='Город построить воду '))

city_electro_kb = InlineKeyboardBuilder()
city_electro_kb.add(
    InlineKeyboardButton(text='⚡️ Построить еще', switch_inline_query_current_chat='Город построить электро '))

city_house_kb = InlineKeyboardBuilder()
city_house_kb.add(
    InlineKeyboardButton(text='🏡 Построить еще', switch_inline_query_current_chat='Город построить дом '))

city_road_kb = InlineKeyboardBuilder()
city_road_kb.add(InlineKeyboardButton(text='🛣 Построить еще', switch_inline_query_current_chat='Город дорога '))

city_build_kb = InlineKeyboardBuilder()
city_build_kb.add(InlineKeyboardButton(text='🏗 Здания', switch_inline_query_current_chat='Город здания '))
