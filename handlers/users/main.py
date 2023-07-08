import secrets
import string
import random
from contextlib import suppress

from aiogram import flags
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from captcha.image import ImageCaptcha

from config import bot_name
from keyboard.help import help_keyboard, back_help_keyboard
from keyboard.main import invite_kb
from loader import bot
from utils.main.cash import to_str
from utils.main.chats import Chat
from utils.main.db import sql
from utils.main.users import User


class solve():
    nameCaptcha = ''


class dialog(StatesGroup):
    captcha = State()


@flags.throttling_key('default')
async def start_handler(message: Message, state: FSMContext):
    if message.chat.id != message.from_user.id:
        Chat(chat=message.chat)

        await message.reply(text=
                            f'👋 Привет! Я — игровой бот Pegasus!\n'
                            '🎲 Начинай играть прямо сейчас! \n'
                            '🎰 Зарабатывай деньги в симуляторе казино, покупай бизнесы, становись самым богатым!\n'
                            '🛡 Создавай клан и грабь магазины/банки/музеи, либо начинай войну с другими кланами ⚔️!\n'
                            '🎁 Открывай кейсы, выходи в топ лучших 🏆! \n'
                            'Все это и многое другое ждёт тебя 😊\n\n'
                            '📌 Пишите боту «Команды» для получения помощи!\n'
                            '💎 В нашей группе Вы увидите частые раздачи и промокоды, не забудь подписться!\n'
                            '<i> Мы рекомендуем ознакомиться с <a href="https://teletype.in/@corching/Termsofuse">пользовательским соглашением</a>, прежде чем продолжить использование данного бота.</i> \n',
                            parse_mode='html',
                            reply_markup=invite_kb.as_markup(), disable_web_page_preview=True)

    else:
        if message.chat.id == message.from_user.id and str(message.text[7:]).isdigit():
            if int(message.text[7:]) == message.from_user.id:
                await bot.send_message(chat_id=message.from_user.id,
                                       text=f'❌ Вы не можете переходите по свой ссылке!\n'
                                       ,
                                       disable_web_page_preview=True)
                return
            try:
                user = User(user=message.from_user, check_ref=True)
            except:
                user = None
            if user is None or user.ref is None:

                try:
                    ref_id = int(message.text[7:])
                    ref = User(id=ref_id)
                except:
                    return

                await state.set_state(dialog.captcha)
                alphabet = string.digits
                image = ImageCaptcha()
                data = ''.join(secrets.choice(alphabet) for _ in range(random.randint(3, 4)))
                image.write(data, 'assets/out.png')
                solve.nameCaptcha = data
                await message.answer('👋🏻 Добро пожаловать, пройди капчу для получения награды!')
                kb = InlineKeyboardBuilder()
                for z in range(5):
                    name = ''.join(secrets.choice(alphabet) for i in range(random.randint(5, 6)))
                    name = str(name)
                    kb.add(InlineKeyboardButton(text=name, callback_data=f'check:{name}:{ref.id}'))
                kb.add(InlineKeyboardButton(text=data, callback_data=f'check:{data}:{ref.id}'))
                photo = FSInputFile("assets/out.png")
                return await message.answer_photo(photo=photo, reply_markup=kb.adjust(2).as_markup())
            else:
                return await message.reply('❗ У вас уже есть рефер!')
        user = User(user=message.from_user)
        user.edit('blocked', False)
        await message.reply(text=
                            f'👋 Привет! Я — игровой бот Pegasus!\n'
                            '🎲 Начинай играть прямо сейчас! \n'
                            '🎰 Зарабатывай деньги в симуляторе казино, покупай бизнесы, становись самым богатым!\n'
                            '🛡 Создавай клан и грабь магазины/банки/музеи, либо начинай войну с другими кланами ⚔️!\n'
                            '🎁 Открывай кейсы, выходи в топ лучших 🏆!\n'
                            'Все это и многое другое ждёт тебя 😊\n\n'
                            '📌 Пишите боту «Команды» для получения помощи!\n'
                            '💎 В нашей группе Вы увидите частые раздачи и промокоды, не забудь подписться!\n\n'
                            '<i> Мы рекомендуем ознакомиться с <a href="https://teletype.in/@corching/Termsofuse">пользовательским соглашением</a>, прежде чем продолжить использование данного бота.</i> \n',

                            parse_mode='html',
                            reply_markup=invite_kb.as_markup(), disable_web_page_preview=True)


async def ref_call_handler(call: CallbackQuery, state: FSMContext):
    check, data, ref_id = call.data.split(':')
    if data == solve.nameCaptcha.lower():
        try:
            user = User(user=call.from_user, check_ref=True)
        except:
            user = None
        if user is None:
            user = User(user=call.from_user)
        try:
            ref = User(id=ref_id)
        except:
            return
        zarefa = sql.execute("SELECT zarefa FROM other", commit=False, fetch=True)[0][0]
        ref.edit('balance', ref.balance + zarefa)
        ref.edit('refs', ref.refs + 1)
        user.edit('ref', ref.id)
        user.edit('balance', user.balance + zarefa)
        with suppress(TelegramBadRequest):
            await bot.send_message(chat_id=ref.id,
                                   text=f'🙂 Дорогой пользователь!\n'
                                        f'Спасибо за приглашение пользователя {user.link}\n'
                                        f'Вам было выдано +{to_str(zarefa)}\n'
                                   ,
                                   disable_web_page_preview=True)
        with suppress(TelegramBadRequest):
            await bot.send_message(chat_id=user.id, text=
            f'👋 Привет! Я — игровой бот Pegasus!\n'
            '🎲 Начинай играть прямо сейчас! \n'
            '🎰 Зарабатывай деньги в симуляторе казино, покупай бизнесы, становись самым богатым!\n'
            '🛡 Создавай клан и грабь магазины/банки/музеи, либо начинай войну с другими кланами ⚔️!\n'
            '🎁 Открывай кейсы, выходи в топ лучших 🏆!\n'
            'Все это и многое другое ждёт тебя 😊\n\n'
            '📌 Пишите боту «Команды» для получения помощи!\n'
            '💎 В нашей группе Вы увидите частые раздачи и промокоды, не забудь подписться!\n\n'
            '<i> Мы рекомендуем ознакомиться с <a href="https://teletype.in/@corching/Termsofuse">пользовательским соглашением</a>, прежде чем продолжить использование данного бота.</i> \n',
                                   parse_mode='html', reply_markup=invite_kb.as_markup(),
                                   disable_web_page_preview=True)
        with suppress(TelegramBadRequest):
            await bot.send_message(chat_id=user.id,
                                   text=f'🙂 Дорогой пользователь!\n'
                                        f'Вы перешли по реферальной ссылки пользователя {ref.link}\n'
                                        f'Вам было выдано +{to_str(zarefa)}\n'
                                   ,
                                   disable_web_page_preview=True)

        await state.clear()
    else:
        await state.clear()
        await call.answer('❌ Неверный ответ на капчу!'
                          'Для повторного решения заново перейдите по ссылки!', show_alert=True)


@flags.throttling_key('default')
async def help_handler(message: Message):
    arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[0].lower() else message.text.split()[
                                                                                                   2:]
    user = User(user=message.from_user)

    if len(arg) == 0:
        return await message.reply(text=actions_help['back'].format(user=user.link),
                                   reply_markup=help_keyboard(user_id=message.from_user.id).as_markup(),
                                   disable_web_page_preview=True)
    elif arg[0].lower() in ['основные']:
        return await message.reply(text=actions_help['main'].format(user=user.link)
                                   , disable_web_page_preview=True)
    elif arg[0].lower() in ['реф', 'реферальная ссылка']:
        return await message.reply(text=f'{user.link}, описание команды:\n'
                                        '💎 В боте есть реферальная система. Работает она так:\n'
                                        '» Вы приглашаете игрока по личной ссылке (получить её можно по команде «Реф»)\n'
                                        '» Другой человек переходит в приложение и, если он не зарегистрирован в боте, Вы получаете игровую валюту\n'
                                        '🎁 Ежедневно ты можешь забрать бонус за приведенных игроков'

                                   , disable_web_page_preview=True)
    elif arg[0].lower() in ['промо', 'промокод']:
        return await message.reply(text=f'{user.link}, описание команды:\n'
                                        '💸 С помощью команды «Промо [промокод]» Вы можете активировать код и получить определенный бонус\n'
                                        '➖ Кол-во активаций любого промокода ограниченно!\n'

                                   , disable_web_page_preview=True)
    elif arg[0].lower() in ['бонус']:
        return await message.reply(text=f'{user.link}, описание команды:\n'
                                        '💎 Команда «Бонус» ежедневно выдает Вам 1 случайный приз.\n'

                                   , disable_web_page_preview=True)
    elif arg[0].lower() in ['дать', 'передать']:
        return await message.reply(text=f'{user.link}, описание команды:\n'
                                        '🤝 Команда «Передать» переводит указанную вами сумму любому игроку: «Передать 225811 1000».\n'

                                   , disable_web_page_preview=True)
    elif arg[0].lower() in ['инвентарь']:
        return await message.reply(text=f'{user.link}, описание команды:\n'
                                        '🎒 В инвентаре содержится все предметы с шахты, фабрики и шопа.\n'
                                        '❓ Команды инвентаря:\n'
                                        '  ➖ Инвентарь - информация о инвентаре\n'
                                        '  ➖ Инвентарь продать [номер предмета] [кол-во] - продать предмет\n'
                                        '  ➖ Инвентарь передать [номер предмета] [кол-во] [ссылка\id] - передать предмета другому игроку\n\n'
                                        '❕ Сокращеная команда «Инв»'

                                   , disable_web_page_preview=True)
    elif arg[0].lower() in ['кредит']:
        return await message.reply(text=f'{user.link}, описание команды:\n'
                                        '💳 Если нужны деньги то вы можете взять их у бота в кредит\n'
                                        '  ➖ Кредит взять\n'
                                        '  ➖ Кредит погасить\n\n'
                                        '❕ каждые 2 часа у вас будут сниматься деньги с основных счетов если вы не выплатите кредит!'
                                   , disable_web_page_preview=True)
    elif arg[0].lower() in ['депозит']:
        return await message.reply(text=f'{user.link}, описание команды:\n'
                                        '〽 Депозит позволяет получать за каждый 12 часов N процентов от суммы на счет\n'
                                        '  ➖ Депозит положить\n'
                                        '  ➖ Депозит снять\n\n'
                                        '❕ Если снять\положить сумму с депозита отчет начнется заново'
                                   , disable_web_page_preview=True)
    elif arg[0].lower() in ['топ']:
        return await message.reply(text=f'{user.link}, описание команды:\n'
                                        '🏆 Команда «Топ» выводит 10 лучших игроков\n'
                                   , disable_web_page_preview=True)
    elif arg[0].lower() in ['ник']:
        return await message.reply(text=f'{user.link}, описание команды:\n'
                                        '✒️ С помощью команды «+Ник» можно выбрать себе ник. Максимальная длина ника: 16, Минимальная: 6 символов.\n'
                                        '➖ Чтобы сделать ник кликабельным/некликабельным введите «Ник вкл» или «Ник выкл» соответственно\n'
                                   , disable_web_page_preview=True)
    elif arg[0].lower() in ['профиль']:
        return await message.reply(text=f'{user.link}, описание команды:\n'
                                        '📒 Команда «Профиль» выводит Вашу игровую статистику.\n'
                                   , disable_web_page_preview=True)
    elif arg[0].lower() in ['баланс']:
        return await message.reply(text=f'{user.link}, описание команды:\n'
                                        '💲 Команда «Баланс» выводит кол-во валюты на Вашем аккаунте.\n'
                                   , disable_web_page_preview=True)
    elif arg[0].lower() in ['браки', 'брак']:
        return await message.reply(text=f'{user.link}, описание команды:\n'
                                        '💞 Используя команды «Брак», «Браки», Вы можете формировать брак/разводиться.\n'
                                        '➖ Брак создать [ссылка/ID игрока] - сделать предложение.\n'
                                        '➖ Брак разорвать - ...\n'
                                        '➖ Брак вывести - снять деньги с брака\n'
                                        '➖ Брак положить - внести деньги в брак\n'
                                        '➖ Брак секс - ...\n'
                                        '➖ Брак награда - В бюджет семью начислят деньги чем больше лвл теи больше награда\n'
                                        '➖ Брак улучшить - улучшает уровень семьи\n'
                                        '➖ Брак ник - изменить ник можно с 4 лвл\n'
                                   , disable_web_page_preview=True)
    elif arg[0].lower() in ['банк', 'bank']:
        return await message.reply(text=f'{user.link}, описание команды:\n'
                                        '💰 В банке можно хранить любое количество валюты.\n'
                                        '➖  Команды банка:\n'
                                        '⠀💳 Банк - выводит сумму в банке\n'
                                        '⠀💵 Банк положить [сумма] - положить в банк\n'
                                        '⠀💸 Банк снять [сумма] - снять со счёта\n'
                                   , disable_web_page_preview=True)
    ##########################################КЛАН#####################################################
    elif arg[0].lower() == 'клан':
        try:
            arg[1].lower()
        except IndexError:
            return await message.reply(text=actions_help['clan'].format(user=user.link)
                                       , disable_web_page_preview=True)
        if arg[1].lower() == 'создать':
            return await message.reply(text=f'{user.link}, описание команды:\n'
                                            '⚜️ С помощью команды «Клан создать» (или «К создать») Вы можете создавать свои кланы.\n'
                                            '➖ Для создания требуется указать название от 4 до 16 символов!\n'
                                       , disable_web_page_preview=True)
        elif arg[1].lower() == 'участники':
            return await message.reply(text=f'{user.link}, описание команды:\n'
                                            '👥 Команда «Участники» выводит весь список игроков, состоящих в Вашем клане.\n'
                                       , disable_web_page_preview=True)
        elif arg[1].lower() == 'кик':
            return await message.reply(text=f'{user.link}, описание команды:\n'
                                            '❌ С помощью команды «Клан кик» глава/соруководитель клана может выгонять других игроков.\n'
                                            '➖ Для исключения введите «Клан кик [игровой ID]»\n'
                                       , disable_web_page_preview=True)
        elif arg[1].lower() == 'тег':
            return await message.reply(text=f'{user.link}, описание команды:\n'
                                            '⚔️ С помощью команды «Клан тег» глава/соруководители могут менять тег перед '
                                            'названием клана.\n '

                                       , disable_web_page_preview=True)
        elif arg[1].lower() == 'покинуть':
            return await message.reply(text=f'{user.link}, описание команды:\n'
                                            '👞 С помощью команды «Клан покинуть» Вы можете выйти из клана.\n'
                                            '📛 Внимание! Если лидер выйдет из клана, то любой кто войдет в клан получит '
                                            'главу а если еть участники то рандомно передастся!'
                                       , disable_web_page_preview=True)
        else:
            return await message.reply(text=actions_help['clan'].format(user=user.link)
                                       , disable_web_page_preview=True)
    ##########################################ГОРОД#####################################################
    elif arg[0].lower() == 'город':
        return await message.reply(text=actions_help['city'].format(user=user.link)
                                   , disable_web_page_preview=True)
    ##########################################ИГРЫ#####################################################
    elif arg[0].lower() == 'игры':
        return await message.reply(text=actions_help['games'].format(user=user.link)
                                   , disable_web_page_preview=True)
    ##########################################РАБОТА#####################################################
    elif arg[0].lower() in ['работа', 'заработок']:
        return await message.reply(text=actions_help['work'].format(user=user.link)
                                   , disable_web_page_preview=True)
    ##########################################ПРОЧЕЕ#####################################################
    elif arg[0].lower() == 'прочее':
        return await message.reply(text=actions_help['other'].format(user=user.link)
                                   , disable_web_page_preview=True)
    ##########################################ИМУЩЕСТВО#####################################################
    elif arg[0].lower() == 'имущество':
        return await message.reply(text=actions_help['imush'].format(user=user.link)
                                   , disable_web_page_preview=True)
    ##########################################УНИКАЛЬНОЕ#####################################################
    elif arg[0].lower() in ['уникальное', 'уникальные']:
        return await message.reply(text=actions_help['unik'].format(user=user.link)
                                   , disable_web_page_preview=True)
    else:
        return await message.reply(text=f'{user.link}, такая команда не найдена 😩'
                                        '❓ Введите «Помощь» для получения всех команд', disable_web_page_preview=True)


actions_help = {
    'back': '''{user}, мои команды:
    
❓ Помощь [команда] - описание команды

💼 Разделы:

Ⓜ Основное       ⚔️ Клан  
🎮 Игры             💫 Уникальное 
🛠️ Работы          🏙 Город 
🚙 Имущество     🗂️ Прочее 

➖➖➖➖➖➖➖➖➖➖➖➖
<b>🗞️ Канал разработки:</b> @pegasusdev
<b>💬 Игровой чат:</b> @chat_pegasus''',

    'main': '''
{user}, мои основные команды:
  <b>💰 Баланс(Б)</b> - Посмотреть баланс
  <b>👤 Профиль(П)</b> - Посмотреть профиль
  <b>😎 Ник</b> [+ник] - Установить никнейм
  <b>👨‍👩‍👦Брак</b> создать [username\id]
     ┗ Брак выйти\положить\снять\секс\награда
  <b>🔔 Ник [ВКЛ/ВЫКЛ]</b> - ВКЛ/ВЫКЛ гипперссылки

  <b>🔝 Топ</b> деньги|банк|депозит|общий|уровень|браки
  <b>🏦 Банк</b> снять|пополнить
  <b>〽 Деп</b> снять|пополнить 
  <b>💸 Кредит</b> взять|погасить

  <b>🎒 Инвентарь</b>
     ┗ Предмет продать|мои|дать [номер][кол-во]
  <b>🤝🏿 Дать</b> - Передать деньги
     ┗ <code>(передать/дать) [сумма][ссылка]</code>
  <b>🎁 Бонус</b> - Ежедневный бонус
  <b>🎁 Промо</b> - Активировать промокод
     ┗ <code>Промо [код]</code> 
  <b>🎁 Промо создать</b> - Создать промокод
     ┗ <code>Промо создать [название][сумма][активации]</code>
  <b>👥 Реф</b> - Реф. система''',

    'games': '''
🕹️ {user}, мои игры:
  <b>🎲 Кубик</b> - Подкинуть кубик
    ┗ Кубик [ставка] [число 1-6]
  <b>🏀️ Баскетбол</b> - Закидовать мяч
   ┗ Баскетбол [ставка]
  <b>🎳 Боулинг</b> - Сбивать кегли
    ┗ Боулинг [ставка]
  <b>🎯 Дартс</b> - Кидать в мишень
    ┗ Дартс [ставка]
  <b>⚽ Футбол</b> - Пинать мяч
    ┗ Футбол [ставка]
  <b>🎰 Спин</b> - Крутить слоты
    ┗ Спин [ставка]
  <b>♣ Казино</b>
    ┗ Казино [ставка]
  <b>🔫 Рулетка</b> - Русская рулетка
    ┗ Рулетка [ставка]
  <b>🃏 Блэкджек</b> 
    ┗ бд\Блэкджек [ставка]
 <b>💣 Сапёр</b> - поиск мин
    ┗ 💣 Сапёр
  <b>❌⭕ Крестики</b> - крестики-нолики
    ┗ Крестики [ответом на сообщение]
      ''',

    'work': '''
🛠️ {user}, команды для заработка:
  <b>⛏️ Шахта</b> - Система шахты 
     ┗ Шахта копать
  <b>🏭 Фабрика</b> - Система Фабрик
     ┗ Фабрика работать
  <b>💪🏿 Работа</b> - Профессия и жизнь
     ┗ Работа [взятка|устроиться] 
  <b>🥷 Ограбить</b> - Система воровства
     ┗ Ограбить [ссылка или название заведения]''',

    'imush': '''
🏘️ {user},
➖ Команды для имущества:
  <b>🏠 Дом</b>
     ┗ Дом снять|сдать|оплатить *[сумма]
  <b>🧑🏿‍💼 Биз</b>
     ┗ Биз снять|сдать|оплатить *[сумма]
  <b>🏎️ Машина</b>
     ┗ Машина снять|оплатить|ехать *[сумма]
  <b>🚁 Вертолёт</b>
    ┗ Вертолёт снять|оплатить|лететь|починить *[сумма]
  <b>✈️ Самолёт</b> 
     ┗ Самолёт снять|оплатить|лететь|починить *[сумма]
  <b>🏍️ Мото</b>
     ┗ мотоцикл снять|оплатить|ехать|починить *[сумма]
  <b>⛵ Яхта</b>
     ┗ Яхта снять|оплатить|плыть|починить *[сумма]
  <b>💻 Компьютер</b>
     ┗ Компьютер снять|починить 
  <b>💲 Налог</b> - Общий налог на всё''',
    'unik': '''
💫 {user},
➖ Команды для уникальное:
 <b>⭐ Биткоин</b> - Система BTC и Ферм
 <b>😇 Префикс</b> - Система префиксов
 <b>💶 Евро</b> - Система евро
 <b>💷 Юань</b> - Система Юань
 <b>👻 Босс</b> - Система боссов
 <b>⚖️ Аукцион</b> - Система торгов
 <b>🔪 Оружейная</b> - Система оружий
 <b>🏪 Шоп</b> - Магазин
''',

    'other': '''
🗂️ {user},
➖ Команды для прочее:
 <b>🪙 Донат</b> - Система доната и привилегий
 <b>📈 Курс биткоина</b>
 <b>🛡️ Щит</b> - Щиты от воровства
 <b>🪙 Кобмен</b> - Обменять коины на доллары
 <b>📟 calc</b> - Калькулятор
 <b>🔮 Шар [фраза]</b> 
 <b>⚖️ Выбери [фраза] или [фраза2]</b>
 <b>📊 Шанс [фраза]</b>
 <b>😇 РП</b> - РП Действия
''',
    'city': '''
{user}, постройте город и зарабатывайте огромные деньги!
➖ Команды для города:
 <b>🏙 Город</b> - информация о Вашем городе
 <b>⚒ Город основать</b> - построить город
 <b>✒️ Город ник [название]</b>
 <b>🏘 Город здания</b> - список зданий в городе
 <b>🏗 Город построить [воду\электро\дом] </b> - построить здание
 <b>🚙 Город дорога [метры]</b> - построить дороги
 <b>💸 Город налог [1-99]</b> - изменить налоги
 <b>💰 Город казна</b> - казна банка 
 ''',
    'clan': '''
{user}, с помощью кланов можно объединяться с другими игроками, устраивать ограбления и получать различные бонусы.
➖ Команды для кланов:
⠀<b>🛡 Клан</b> - информация о клане
⠀<b>✏️ Клан тег [вкл/выкл]</b> - вкл/выкл отображение клана в нике
⠀<b>🏆 Кланы</b> - список кланов 
⠀<b>⚜️ Клан создать [название]</b>
⠀<b>👥 Клан участники</b>
⠀<b>❌ Клан кик [ID]</b> - выгнать игрока
⠀<b>⚔️ Клан преф [метка]</b> - символ клана
⠀<b>👞 Клан покинуть</b>
⠀<b>⤴️ Клан улучшить</b> - улучшить клан
⠀<b>📢 Клан название</b> - смена названия клана
⠀<b>🔷 Клан повысить</b> - повысить звание игроку
⠀<b>🔻 Клан понизить</b> - понизить звание игроку
  <b>📥 Клан положить</b> - пополнить казну
  <b>📤 Клан снять</b> - снять с казны
⠀<b>📋 Клан инфо [ID]</b> - информация об участнике
⠀<b>👥 Клан участники</b> - список участников клана
⠀<b>🔈 Клан заявки</b> - принять приглашения в клан
⠀<b>✔️ Клан войти [ID клана]</b> - вступить в клан

⠀<b>🗡 Кв</b> - информация о текущей клановой войне

 '''
}


@flags.throttling_key('default')
async def help_call_handler(call: CallbackQuery):
    action = call.data.split('_')[1]
    action2 = action.split(':')
    text = actions_help[action2[0]]
    user = User(user=call.from_user)
    if int(action2[1]) == call.from_user.id:
        try:
            return await call.message.edit_text(text=text.format(user=user.link),
                                                reply_markup=back_help_keyboard(action2[1]).as_markup() if action2[
                                                                                                               0] != 'back' else help_keyboard(
                                                    action2[1]).as_markup(), disable_web_page_preview=True)
        except:
            return await call.answer('😎')
    else:
        return await call.answer('Не твоё!')
