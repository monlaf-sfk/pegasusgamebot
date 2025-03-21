from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, KeyboardButton, InlineKeyboardMarkup
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from config import bot_name

invite_kb = InlineKeyboardBuilder()
invite_kb.add(InlineKeyboardButton(text='🧑‍🎄 Чат', url='https://t.me/pegasus_talk'))
invite_kb.add(InlineKeyboardButton(text='📯 Канал', url='t.me/pegasusdev'))
invite_kb.add(InlineKeyboardButton(text='🪄 Добавить в чат', url=f'https://t.me/{bot_name}?startgroup=1'))
invite_kb.adjust(2)

check_ls_kb = InlineKeyboardBuilder()
check_ls_kb.add(InlineKeyboardButton(text='🔗 Перейти в бота', url=f'https://t.me/{bot_name}'))


def quest_pag_kb(user_id, current_page, total_pages):
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text='❓ Подсказки', callback_data=f'quest_advise_{user_id}'))
    kb.add(InlineKeyboardButton(text='🔄 Новые квесты', callback_data=f'quest_reload_{user_id}'))
    kb.add(InlineKeyboardButton(text='🏆 Достижения', callback_data=f'quest_achiv_{user_id}'))

    if current_page > 1:
        kb.add(
            InlineKeyboardButton(text="⬅️ Назад", callback_data=f"pag_quest_prev_{current_page - 1}_{user_id}"))

    if current_page < total_pages:
        kb.add(
            InlineKeyboardButton(text="➡️ Вперед", callback_data=f"pag_quest_next_{current_page + 1}_{user_id}"))

    kb.adjust(2, 1, 2)
    return kb.as_markup()


def quest_kb(user_id):
    kb = InlineKeyboardBuilder()

    kb.add(InlineKeyboardButton(text='❓ Подсказки', callback_data=f'quest_advise_{user_id}'))
    kb.add(InlineKeyboardButton(text='🔄 Новые квесты', callback_data=f'quest_reload_{user_id}'))
    kb.add(InlineKeyboardButton(text='🏆 Достижения', callback_data=f'quest_achiv_{user_id}'))
    kb.adjust(2)
    return kb.as_markup()


def marry_kb(user1, _):
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text='✅ Принять', callback_data=f'maccept_{user1}'))
    kb.add(InlineKeyboardButton(text='❌ Отклонить', callback_data=f'mdecline_{user1}'))
    invite_kb.adjust(1)
    return kb.as_markup()


def uchas(count, button_name):
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text=f'({count}){button_name}', callback_data='raz'))
    return kb


admin_kb = InlineKeyboardBuilder()
admin_kb.add(InlineKeyboardButton(text='👤 Рассылка пользователям', callback_data='rass_users'))
admin_kb.add(InlineKeyboardButton(text='💭 Рассылка по чатам', callback_data='rass_chats'))
admin_kb.add(InlineKeyboardButton(text='🔗 Запланировать бд', callback_data='plan'))
admin_kb.add(InlineKeyboardButton(text='📃 Список чатов', callback_data='allchats'))
admin_kb.add(InlineKeyboardButton(text='💬️ ВДЗУ', callback_data='wdzy'))
admin_kb.add(InlineKeyboardButton(text='🎁 Раздача', switch_inline_query_current_chat='/gift'))
admin_kb.adjust(2)
# admin_kb.add(InlineKeyboardButton(text='💾 Получить БД', callback_data='get_db'))

cancel = ReplyKeyboardBuilder()
cancel.add(KeyboardButton(text='❌'))
remove = ReplyKeyboardRemove()

donate_kb = InlineKeyboardBuilder()
donate_kb.add(InlineKeyboardButton(text='🎄 Получить коины', switch_inline_query_current_chat="задонатить"))

donate_kbi = InlineKeyboardBuilder()
donate_kbi.add(InlineKeyboardButton(text='🎄 Получить коины', callback_data='donate'))

back_donate = InlineKeyboardBuilder()
back_donate.add(InlineKeyboardButton(text='🅰️ Написать админу', url='https://t.me/corching'))
back_donate.add(InlineKeyboardButton(text='🎄 Вернуться назад', callback_data='donate'))
back_donate.adjust(1)

link_to_owner = InlineKeyboardBuilder()
link_to_owner.add(InlineKeyboardButton(text='🅰️ Написать админу', url='https://t.me/corching'))


def unmute_kb(user_id: int):
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text='🔗 Размутить', callback_data=f'unmute_{user_id}'))
    return kb


def unban_kb(user_id: int):
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text='🔗 Разбанить', callback_data=f'unban_{user_id}'))
    return kb


donates_kb = InlineKeyboardBuilder()
donates_kb.add(InlineKeyboardButton(text='👛 CryptoBot', callback_data='donate_crypto'))
donates_kb.add(InlineKeyboardButton(text='🥝 Qiwi', callback_data='donate_qw'))
donates_kb.add(InlineKeyboardButton(text='💎 Crystal', callback_data='donate_crystal'))
donates_kb.add(InlineKeyboardButton(text='🆗 Payok', callback_data='donate_payok'))
donates_kb.add(InlineKeyboardButton(text='🅰️ Aaio', callback_data='donate_aaio'))
donates_kb.adjust(3)

inv_kb = InlineKeyboardBuilder()
inv_kb.add(InlineKeyboardButton(text='💲 Продать всё', switch_inline_query_current_chat='Инв продать всё'))


def status_kb_func(id):
    status_kb = InlineKeyboardBuilder()
    status_kb.add(InlineKeyboardButton(text='🔱 Статус', callback_data=f'status:{id}'))
    return status_kb


def status_back_kb_func(id):
    status_back_kb = InlineKeyboardBuilder()
    status_back_kb.add(InlineKeyboardButton(text='🔙 Назад', callback_data=f'status_back_{id}'))
    return status_back_kb


prefix_buy_kb = InlineKeyboardBuilder()
prefix_buy_kb.add(InlineKeyboardButton(text='⭐ Купить префикс', switch_inline_query_current_chat='Префикс купить '))


def top_kb_func(id):
    top_kb = InlineKeyboardBuilder()
    top_kb.add(InlineKeyboardButton(text='💲 Деньги', callback_data=f'top_балансу_{id}'))
    top_kb.add(InlineKeyboardButton(text='💳 Депозит', callback_data=f'top_депозит_{id}'))
    top_kb.add(InlineKeyboardButton(text='🏦 Банк', callback_data=f'top_банк_{id}'))
    top_kb.add(InlineKeyboardButton(text='📢 Общий', callback_data=f'top_общ_{id}'))
    top_kb.add(InlineKeyboardButton(text='⭐ LVL', callback_data=f'top_лвл_{id}'))
    top_kb.add(InlineKeyboardButton(text='👥 Реф', callback_data=f'top_реф_{id}'))
    top_kb.add(InlineKeyboardButton(text='🛡 Клан', callback_data=f'top_клан_{id}'))
    top_kb.adjust(3)
    return top_kb


def top_back_func(id):
    top_kb_back_kb = InlineKeyboardBuilder()
    top_kb_back_kb.add(InlineKeyboardButton(text='🔙 Назад', callback_data=f'topback_{id}'))
    return top_kb_back_kb


def ref_share_func(id):
    ref_share = InlineKeyboardBuilder()
    ref_share.add(InlineKeyboardButton(text='💲 Поделиться',
                                       switch_inline_query=f'Привет , смотри какой интересный бот https://t.me/{bot_name}?start={id}'))
    return ref_share


def promo_switch(id, switch, name):
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text=f'{"❌ ВЫКЛ" if switch else "✅ ВКЛ"}', callback_data=f'promo_{id}_{name}'))
    return kb


def imush_kb_func(id):
    imush_kb = InlineKeyboardBuilder()
    imush_kb.add(InlineKeyboardButton(text='➖ Имущество', callback_data=f'imush:{id}'))
    return imush_kb


def imush_back_func(id):
    imush_backkb = InlineKeyboardBuilder()
    imush_backkb.add(InlineKeyboardButton(text='🔙 Назад', callback_data=f'imushback_{id}'))
    return imush_backkb


class SettingsCallback(CallbackData, prefix="settings"):
    user_id: int
    action: str


class SettingsNotifiesCallback(CallbackData, prefix="settingsNotifies"):
    user_id: int
    action: str


class SettingsNickCallback(CallbackData, prefix="settingsNick"):
    user_id: int
    action: str


def settings_kb(user_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text=f"🔔 Уведомления",
                             callback_data=SettingsCallback(action="notifies", user_id=user_id).pack())
    )
    keyboard.add(
        InlineKeyboardButton(text=f"✏️ Никнейм",
                             callback_data=SettingsCallback(action="nickname", user_id=user_id).pack()))

    keyboard.adjust(1)
    return keyboard.as_markup()


def settings_action_kb(user_id, action):
    keyboard = InlineKeyboardBuilder()
    if action == 'notifies':
        keyboard.add(
            InlineKeyboardButton(text=f"💸 Переводы",
                                 callback_data=SettingsNotifiesCallback(action="pay", user_id=user_id).pack())
        )
        keyboard.add(
            InlineKeyboardButton(text=f"🏙 Города",
                                 callback_data=SettingsNotifiesCallback(action="city", user_id=user_id).pack()))
        keyboard.add(
            InlineKeyboardButton(text=f"💞 Браки",
                                 callback_data=SettingsNotifiesCallback(action="marry", user_id=user_id).pack())
        )
        keyboard.add(
            InlineKeyboardButton(text=f"🛡️ Клан",
                                 callback_data=SettingsNotifiesCallback(action="clan", user_id=user_id).pack()))
        keyboard.add(
            InlineKeyboardButton(text=f"⚙ Настройки",
                                 callback_data='settings_user'))

        keyboard.adjust(2)
    else:
        keyboard.add(
            InlineKeyboardButton(text=f"👆 Вкл. гиперссылку",
                                 callback_data=SettingsNickCallback(action="on_hyperlink", user_id=user_id).pack())
        )
        keyboard.add(
            InlineKeyboardButton(text=f"👓 Выкл. гиперссылку",
                                 callback_data=SettingsNickCallback(action="off_hyperlink", user_id=user_id).pack())
        )
        keyboard.add(
            InlineKeyboardButton(text=f"🛡️ Вкл. клан в нике",
                                 callback_data=SettingsNickCallback(action="on_clanteg", user_id=user_id).pack()))
        keyboard.add(
            InlineKeyboardButton(text=f"⚔ Выкл. клан в нике",
                                 callback_data=SettingsNickCallback(action="off_clanteg", user_id=user_id).pack()))
        keyboard.add(
            InlineKeyboardButton(text=f"⚙ Настройки",
                                 callback_data='settings_user'))
        keyboard.adjust(2)

    return keyboard.as_markup()


settings_switch_kb = InlineKeyboardBuilder()
settings_switch_kb.add(InlineKeyboardButton(text='💸 Переводы', switch_inline_query_current_chat='Увед п'))
settings_switch_kb.add(InlineKeyboardButton(text='🏙 Города', switch_inline_query_current_chat='Увед г'))
settings_switch_kb.add(InlineKeyboardButton(text='💞 Браки', switch_inline_query_current_chat='Увед б'))
settings_switch_kb.add(InlineKeyboardButton(text='🛡️ Клан', switch_inline_query_current_chat='Увед к'))
settings_switch_kb.adjust(2)

settings2_switch_kb = InlineKeyboardBuilder()
settings2_switch_kb.add(InlineKeyboardButton(text='👆 Вкл. гиперссылку', switch_inline_query_current_chat='Ник вкл'))
settings2_switch_kb.add(InlineKeyboardButton(text='👓 Выкл. гиперссылку', switch_inline_query_current_chat='Ник выкл'))
settings3_switch_kb = settings2_switch_kb.copy().adjust(1)

settings2_switch_kb.add(
    InlineKeyboardButton(text='🛡️ Вкл. клан в нике', switch_inline_query_current_chat='Клан тег вкл'))
settings2_switch_kb.add(
    InlineKeyboardButton(text='⚔ Выкл. клан в нике', switch_inline_query_current_chat='Клан тег выкл'))
settings4_switch_kb = InlineKeyboardMarkup(
    inline_keyboard=[[sublist] for sublist in settings2_switch_kb.export()[0][2:]])
settings2_switch_kb.adjust(2)


def settings_notifies_kb(user_id):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(
        InlineKeyboardButton(text=f"🔔 Уведомления",
                             callback_data=SettingsCallback(action="notifies", user_id=user_id).pack())
    )
    keyboard.adjust(1)

    return keyboard.as_markup()


def marry_divorce_kb(user_id, time):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(
        InlineKeyboardButton(text=f"✅ Подтвердить",
                             callback_data=f'divorce:{user_id}:{time}')
    )
    keyboard.adjust(1)
    return keyboard.as_markup()
