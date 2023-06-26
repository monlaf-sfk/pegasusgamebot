import decimal
import random
import re
import time
from datetime import datetime

from aiogram import flags
from aiogram.client import bot
from aiogram.utils.keyboard import InlineKeyboardBuilder

from filters.users import flood_handler
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery

from keyboard.clans import member_kb, info_clan

from config import bot_name
from utils.clan.clan import Clanuser, Clan, status_clan
from utils.logs import writelog
from utils.main.cash import get_cash, to_str
from utils.main.db import sql, timetostr
from utils.main.users import User


@flags.throttling_key('default')
async def clan_handler(message: Message):
    flood = await flood_handler(message)
    if flood:
        arg = message.text.split()[1:] if not bot_name.lower() in message.text.split()[
            0].lower() else message.text.split()[2:]
        user = User(id=message.from_user.id)
        try:
            clanuser = Clanuser(user_id=message.from_user.id)
        except:
            clanuser = None

        if len(arg) == 0 or arg[0].lower() in ['мой', 'моя', 'моё']:
            if clanuser is None:
                return await message.reply('❌ У вас нет клана :(')
            clan = Clan(clan_id=clanuser.id_clan)
            lol = datetime.now() - clan.reg_date
            xd = f'{lol.days} дн.' if lol.days > 0 else f'{int(lol.total_seconds() // 3600)} час.' \
                if lol.total_seconds() > 59 else f'{int(lol.seconds)} сек.'

            text = f'{user.link}, информация о Вашем клане:\n' \
                   f'✏️ Название: {clan.name}\n' f'🛡 Уровень: {clan.level}\n' \
                   f'🔎 ID клана: {clan.id}\n'f'👑 Ваш ранг: {status_clan[clanuser.status]["name"]}\n' \
                   f'🔒 Тип: {"Закрыт" if clan.type == 1 else "Открыт" if clan.type == 0 else "По Приглашению"}\n' \
                   f'♨ Префикс: {clan.prefix if clan.prefix != "" else "Нету"}\n' \
                   f'➖➖➖➖➖➖➖➖\n'f'🏆 Рейтинг: {clan.rating}\n' \
                   f'💰 В казне: {clan.kazna}\n'f'🗡 Сил: {clan.power}\n' \
                   f'🥇 Побед: {clan.win}\n'f'💀 Проигрышей: {clan.lose}\n' \
                   f'➖➖➖➖➖➖➖➖➖\n'f' 👥 Участники ({clan.members}/50)\n' \
                   f'📅 Дата: {clan.reg_date}:({xd})'
            # f'➖➖➖➖➖➖➖➖\n'f'💵 Ограбление: \n'\
            return await message.reply(text=text, reply_markup=member_kb(clanuser.id_clan).as_markup(),
                                       disable_web_page_preview=True)
        elif arg[0].lower() in ['создать', 'основать']:
            if clanuser:
                return await message.reply('❌ У вас уже есть клан... Предатель найден!')
            price = 10000000

            if price > user.balance:
                return await message.reply(
                    f'❌ Недостаточно средств на руках! Нужно еще: {to_str(price - user.balance)}')

            try:
                name = re.sub('''[@"'%<>💎👨‍🔬🌟⚡👮‍♂➪👾🥲⛏😎👑💖🐟🍆😈🏿🐥👶🏿🇷🇺🇺🇦]''', '', arg[1])
            except:
                return await message.reply('❌ Используйте: <code>Клан создать {название}</code>')
            if len(name) < 4 or len(name) > 16:
                return await message.reply('❌ Длина больше 16 или меньше 4. Запрещены символы.')
            Clan.create(message.from_user.id, name)
            clan = Clan(owner=message.from_user.id)
            Clanuser.create(message.from_user.id, clan.id)
            await message.reply(f'✅ Вы успешно создали клан {name}', disable_web_page_preview=True)
            # await writelog(message.from_user.id, f'Приючение {user2.link}')
            return
        elif arg[0].lower() in ['выйти', 'удалить', 'покинуть']:
            if clanuser is None:
                return await message.reply('❌ У вас нет клана :(')
            clan = Clan(clan_id=clanuser.id_clan)
            if clanuser.status == 2:
                clanuser.dellclan()
                clan.edit('members', clan.members - 1)
                clan.edit('owner', None)
                if clan.members > 0:
                    user_ids = sql.execute(query=f'SELECT id FROM clan_users WHERE id_clan={clan.id}', commit=False,
                                           fetch=True)
                    list_user = []
                    for user in user_ids:
                        list_user.append(f"{user[0]}")

                    random_index = random.randrange(len(list_user))
                    new_id = int(list_user[random_index])
                    clan.edit('owner', new_id)
                    clanuser = Clanuser(user_id=new_id)
                    clanuser.edit('status', 2)

            else:
                clanuser.dellclan()
                clan.edit('members', clan.members - 1)

            return await message.reply('✅ Вы успешно покинули')


        elif arg[0].lower() in ['снять', 'вывести']:
            if clanuser.id_clan is None:
                return await message.reply('❌ У вас нет клана :(')
            clan = Clan(clan_id=clanuser.id_clan)
            summ = 0
            try:
                summ = get_cash(arg[1])
            except:
                pass

            if summ <= 0:
                return await message.reply('❌ Минимум $1')

            elif summ > clan.kazna:
                return await message.reply('❌ Недостаточно средств на счету клана!')
            if clanuser.status <= 0:
                return await message.reply('❌ Низкий ранг!')
            sql.executescript(f'UPDATE users SET balance = balance + {summ} WHERE id = {message.from_user.id};\n'
                              f'UPDATE clans SET kazna = kazna - {summ} WHERE id = {clanuser.id_clan}',
                              True, False)

            await message.reply(f'✅ Вы успешно сняли {to_str(summ)} с бюджета клана!')
            await writelog(message.from_user.id, f'Снятие {to_str(summ)} с бюджета клана')
            return
        elif arg[0].lower() in ['положить', 'вложить', 'пополнить']:
            if clanuser is None:
                return await message.reply('❌ У вас нет клана :(')
            summ = 0
            try:
                summ = get_cash(arg[1])
            except:
                pass
            if user.payban:
                return await message.reply('❌ На ваш аккаунт наложено ограничение на переводы !')
            if summ <= 0:
                return await message.reply('❌ Минимум $1')

            elif summ > user.balance:
                return await message.reply('❌ Недостаточно средств на руках!')

            sql.executescript(f'UPDATE users SET balance = balance - {summ} WHERE id = {message.from_user.id};\n'
                              f'UPDATE clans SET kazna = kazna + {summ} WHERE id = {clanuser.id_clan}',
                              True, False)

            await message.reply(f'✅ Вы успешно пополнили бюджет клана на +{to_str(summ)}')
            await writelog(message.from_user.id, f'Пополнение {to_str(summ)} в бюджет клана')
            return
        elif arg[0].lower() in ['сила', 'усилить']:
            if clanuser is None:
                return await message.reply('❌ У вас нет клана :(')
            summ = 0
            try:
                summ = get_cash(arg[1])
            except:
                pass
            price = 100000 * summ
            if summ <= 0:
                return await message.reply('❌ Минимум 1🗡')

            elif price > user.balance:
                return await message.reply(
                    f'❌ Недостаточно средств на руках! Нужно еще: {to_str(price - user.balance)}')

            sql.executescript(f'UPDATE users SET balance = balance - {price} WHERE id = {message.from_user.id};\n'
                              f'UPDATE clans SET power = power + {summ} WHERE id = {clanuser.id_clan}',
                              True, False)

            await message.reply(f'✅ Вы успешно усилили свою крепость  +{summ}🗡')
            await writelog(message.from_user.id, f'усилили свою крепость +{to_str(summ)}🗡')
            return

        elif arg[0].lower() in ['улучшить']:
            if not clanuser:
                return await message.reply('❌ У вас нет клана :(')
            clan = Clan(clan_id=clanuser.id_clan)
            if clan.level == 3:
                return await message.reply(
                    f'У вашего клана максимальный уровень!')
            price = 10000000 * (clan.level + 1)
            if user.balance < price:
                return await message.reply(
                    f'💲 Недостаточно денег на руках для улучшения клана. Нужно: {to_str(price)}')

            query = f'UPDATE users SET balance = balance - {price} WHERE id = {message.from_user.id};\n' \
                    f'UPDATE clans SET level = level + 1 WHERE id = {clanuser.id_clan};'

            sql.executescript(query=query, commit=True, fetch=False)

            return await message.reply(f'✅ Вы улучшили уровень клана на +1, текущий уровень: {clan.level + 1}')
        elif arg[0].lower() in ['закрыть', 'открыть', 'пригл']:
            if not clanuser:
                return await message.reply('❌ У вас нет клана :(')
            clan = Clan(clan_id=clanuser.id_clan)

            if clanuser.status <= 1:
                return await message.reply('❌ Низкий ранг!')
            if arg[0].lower() in ['закрыть']:
                clan.edit('type', 1)
                return await message.reply(f'✅ Клан закрыт')
            if arg[0].lower() in ['открыть']:
                clan.edit('type', 0)
                return await message.reply(f'✅ Клан открыт')
            if arg[0].lower() in ['пригл']:
                clan.edit('type', 2)
                return await message.reply(f'✅ Вступление по приглашению')
        elif arg[0].lower() in ['вступить']:
            if clanuser:
                return await message.reply('❌ У вас уже есть клан !')
            try:
                clan = Clan(clan_id=arg[1])
            except:
                return await message.reply('❌ Ошибка. Не найден клан с таким айди!')
            if clan.owner == None and clan.members == 0:
                Clanuser.create(message.from_user.id, clan.id)
                clan.edit('members', clan.members + 1)
                clan.edit('owner', message.from_user.id)
                return await message.reply(f'✅ Вы вступили в клан {clan.name}\n'
                                           f'Прошлый владелц струсил и убежал и теперь ты стал главой клана!')
            if clan.type == 0:
                Clanuser.create2(message.from_user.id, clan.id)
                clan.edit('members', clan.members + 1)
                return await message.reply(f'✅ Вы вступили в клан {clan.name}')
            if clan.type == 1:
                return await message.reply(f'❌ Клан {clan.name} закрыт!')
            if clan.type == 2:
                clan.add_invites(message.from_user.id)
                await message.reply(f'Заявка в клан отправлена!!')
                try:
                    await bot.send_message(clan.owner, f'Вам поступила заявка в клан!')
                except:
                    pass
                return
        elif arg[0].lower() in ['заявки']:
            if clanuser is None:
                return await message.reply('❌ У вас нет клана :(')
            clan = Clan(clan_id=clanuser.id_clan)
            if clanuser.status <= 0:
                return await message.reply('❌ Низкий ранг!')
            clan.invites = list(clan.invites)
            if clan.invites[0] != '':
                text = '🛃 Заявки:\n'
                keyboard = InlineKeyboardBuilder()
                for i in clan.invites:
                    user = User(id=int(i))
                    text += f'👤 Пользователь: {user.link}\n'
                    button = InlineKeyboardButton(text=f'{user.first_name}',
                                                  callback_data=f"invite_{int(i)} {clan.id} {clanuser.id}")
                    keyboard.add(button)
                return await message.reply(text=text, reply_markup=keyboard.adjust(1).as_markup(),
                                           disable_web_page_preview=True)
            else:
                return await message.reply('❌ На данный момент нету заявок!')
        elif arg[0].lower() in ['повысить']:
            if clanuser is None:
                return await message.reply('❌ У вас нет клана :(')
            if clanuser.status <= 1:
                return await message.reply('❌ Низкий ранг!')
            try:
                if arg[1].isdigit():
                    id = int(arg[1])
                    try:
                        clanuser2 = Clanuser(user_id=id)
                    except:
                        return await message.reply(
                            text='❕ Он не состоит в вашем клане!')
                    if clanuser2.status + 1 == 2:
                        return await message.reply(text='❕ У пользователя макс. ранг!')

                    if clanuser.id_clan != clanuser2.id_clan and clanuser.id != id:
                        return await message.reply(
                            text='❕ Он не состоит в вашем клане!')
                    clanuser2.edit('status', clanuser2.status + 1)
                    return await message.reply(text='✅ Вы успешно повысили игрока!')
                else:

                    return await message.reply(text='🆔 Введите id пользователя которого хотите повысить\понизить!\n'
                                                    '➖ Клан повысить\понизить id')
            except Exception as e:
                print(e)
                return await message.reply(text='🆔 Введите id пользователя которого хотите повысить\понизить!\n'
                                                '➖ Клан повысить\понизить id')
        elif arg[0].lower() in ['понизить']:
            if clanuser is None:
                return await message.reply('❌ У вас нет клана :(')
            if clanuser.status <= 1:
                return await message.reply('❌ Низкий ранг!')
            try:
                if arg[1].isdigit():
                    id = arg[1]
                    try:
                        clanuser2 = Clanuser(user_id=id)
                    except:
                        return await message.reply(
                            text='❕ Он не состоит в вашем клане!')
                    if clanuser2.status - 1 < 0:
                        return await message.reply(text='❕ У пользователя мин. ранг!')

                    if clanuser.id_clan != clanuser2.id_clan and clanuser.id != id:
                        return await message.reply(
                            text='❕ Он не состоит в вашем клане!')
                    clanuser2.edit('status', clanuser2.status - 1)
                    return await message.reply(text='✅ Вы успешно понизили игрока!')
                else:
                    return await message.reply(text='🆔 Введите id пользователя которого хотите повысить\понизить!\n'
                                                    '➖ Клан повысить\понизить id')
            except:
                return await message.reply(text='🆔 Введите id пользователя которого хотите повысить\понизить!\n'
                                                '➖ Клан повысить\понизить id')

        elif arg[0].lower() in ['кик']:
            if clanuser is None:
                return await message.reply('❌ У вас нет клана :(')
            if clanuser.status <= 0:
                return await message.reply('❌ Низкий ранг!')
            try:
                clan = Clan(clan_id=clanuser.id_clan)
                if arg[1].isdigit():
                    id = arg[1]
                    try:
                        clanuser2 = Clanuser(user_id=id)
                    except:
                        return await message.reply(
                            text='❕ Он не состоит в вашем клане!')

                    if clanuser.id_clan != clanuser2.id_clan and clanuser.id != id:
                        return await message.reply(
                            text='❕ Он не состоит в вашем клане!')
                    clanuser2.dellclan()
                    clan.edit('members', clan.members - 1)
                    return await message.reply(text='✅ Вы успешно кикнули игрока!')
                else:
                    return await message.reply(text='🆔 Введите id пользователя которого хотите кикнуть!\n'
                                                    '➖ Клан кикнуть id')
            except:
                return await message.reply(text='🆔 Введите id пользователя которого хотите кикнуть!\n'
                                                '➖ Клан кикнуть id')
        elif arg[0].lower() in ['участники']:
            if clanuser is None:
                return await message.reply('❌ У вас нет клана :(')
            clan = Clan(clan_id=clanuser.id_clan)
            user = User(id=message.from_user.id)
            user_ids = sql.execute(query=f'SELECT id FROM clan_users WHERE id_clan={clan.id}', commit=False, fetch=True)
            text = f"{user.link}, участники клана [{clan.name}]\n"
            for user in user_ids:
                user1 = User(id=user[0])
                clanuser = Clanuser(user_id=user[0])
                if clanuser.status == 0:
                    text += f'[👤]{user1.link}(<code>{user1.id}</code>)— 🏆 {clanuser.rating}\n'
                if clanuser.status == 1:
                    text += f'[💎]{user1.link}(<code>{user1.id}</code>)— 🏆 {clanuser.rating}\n'
                if clanuser.status == 2:
                    text += f'[👑]{user1.link}(<code>{user1.id}</code>)— 🏆 {clanuser.rating}\n'
            return await message.reply(text=text, disable_web_page_preview=True)
        elif arg[0].lower() in ['атака']:
            if clanuser is None:
                return await message.reply('❌ У вас нет клана :(')
            if clanuser.status <= 0:
                return await message.reply('❌ Низкий ранг!')
            try:
                if arg[1].isdigit():
                    id = int(arg[1])
                    clan = Clan(clan_id=clanuser.id_clan)
                    user = User(id=clanuser.id)
                    try:
                        сlan2 = Clan(clan_id=id)
                    except:
                        return await message.reply(
                            text='❕ Нету клана с таким id')
                    if clan.level <= 2:
                        return await message.reply(
                            text='❕ Необходима уровень клана 3!\n'
                                 '➖ Клан улучшить')
                    if сlan2.level <= 2:
                        return await message.reply(
                            text='❕ Уровень клана противника недостаточен для участь в войне!')
                    if clan.id == сlan2.id:
                        return await message.reply(
                            text='❕ Вы не можете атаковать самого себя!')
                    if сlan2.power < 1 or clan.power < 1:
                        return await message.reply(
                            text='❕ У даного клана мало сил или же у вас!')

                    if clan.last_attack != None and (decimal.Decimal(time.time()) - clan.last_attack) < 3600 * 12:
                        return await message.reply('⌚ Вы недавно уже атаковали, ващим товарищам нужно восстановиться!\n'
                                                   f'Через: {timetostr(3600 * 12 + clan.last_attack - decimal.Decimal(time.time()))}')

                    if clan.power > сlan2.power:
                        await message.reply(text=f'⚔️{user.link} атакавал клан {сlan2.name}\n'
                                                 '📋Результат:\n'
                                                 f'🏅 Поздравляю с победой над кланом {сlan2.name}!\n'
                                                 f'🗡 Потерено сил (-{сlan2.power})', disable_web_page_preview=True)
                        clan.editmany(win=clan.win + 1, power=clan.power - сlan2.power, last_attack=time.time())
                        сlan2.editmany(lose=clan.lose + 1, power=0)

                        return
                    elif clan.power < сlan2.power:
                        await message.reply(text=f'⚔️{user.link} атакавал клан {сlan2.name}\n'
                                                 '📋Результат:\n'
                                                 f'💀 К сожелению вражеский клан оказался сильнее\n'
                                                 f'🗡 Потерены все силы', disable_web_page_preview=True)
                        сlan2.editmany(win=сlan2.win + 1, power=сlan2.power - clan.power)
                        clan.editmany(lose=clan.lose + 1, power=0, last_attack=time.time())
                        return
                else:

                    return await message.reply(text='🆔 Введите id клана которого хотите атаковать!\n'
                                                    '➖ Клан атака id')
            except:
                return await message.reply(text='🆔 Введите id клана которого хотите атаковать!\n'
                                                '➖ Клан атака id')
        elif arg[0].lower() in ['инфо']:
            if clanuser is None:
                return await message.reply('❌ У вас нет клана :(')
            if clanuser.status <= 0:
                return await message.reply('❌ Низкий ранг!')
            try:
                if arg[1].isdigit():
                    id = int(arg[1])
                    try:
                        clanuser2 = Clanuser(user_id=id)
                    except:
                        return await message.reply(
                            text='❕ Он не состоит в вашем клане!')

                    if clanuser.id_clan != clanuser2.id_clan and clanuser.id != id:
                        return await message.reply(
                            text='❕ Он не состоит в вашем клане!')
                    user = User(id=id)
                    clan = Clan(clan_id=clanuser.id_clan)
                    if clan.owner == id:
                        return await message.reply(text=f'👤 Игрок: {user.link}\n'
                                                        f'👑 Ранг: {status_clan[clanuser2.status]["name"]}\n'
                                                        f'🏆 Рейтинг: {clanuser2.rating}🏆\n'
                                                        f'📅 Дата рег: {clanuser2.reg_date}\n')
                    return await message.reply(text=f'👤 Игрок: {user.link}\n'
                                                    f'👑 Ранг: {status_clan[clanuser2.status]["name"]}\n'
                                                    f'🏆 Рейтинг: {clanuser2.rating}🏆\n'
                                                    f'📅 Дата рег: {clanuser2.reg_date}\n'
                                               , reply_markup=info_clan(id, clanuser.id, clanuser2.status).adjust(
                            1).as_markup(), disable_web_page_preview=True)
                else:
                    return await message.reply(text='🆔 Введите id игрока !\n'
                                                    '➖ Клан инфо id')
            except:
                return await message.reply(text='🆔 Введите id игрока !\n'
                                                '➖ Клан инфо id')

        elif arg[0].lower() in ['преф', 'префикс']:
            if not clanuser:
                return await message.reply('❌ У вас нет клана :(')
            clan = Clan(clan_id=clanuser.id_clan)
            if clanuser.status <= 0:
                return await message.reply('❌ Низкий ранг!')
            try:
                name = re.sub('''[@"'%<>💎👨‍🔬🌟⚡👮‍♂➪👾🥲⛏😎👑💖🐟🍆😈🏿🐥👶🏿🇷🇺🇺🇦]''', '', arg[1])
            except:
                return await message.reply('❌ Используйте: <code>Клан преф {название}</code>')
            if len(name) > 4 or len(name) < 3:
                return await message.reply('''❌ Длина 4-3. Запрещеные символы.''')
            prefixes = sql.execute("SELECT prefix FROM clans", fetch=True)

            if name.upper() in str(prefixes):
                return await message.reply(
                    '''❌ Данный префикс уже занят''')
            clan.edit('prefix', name.upper())
            return await message.reply(
                f'❕ Успешно сменили префикс на: [{name.upper()}]')
        elif arg[0].lower() in ['тег']:
            if not clanuser:
                return await message.reply('❌ У вас нет клана :(')
            if arg[1].lower() == 'выкл':
                user.edit('clan_teg', False)
                text = f'{user.link}, отображение клана в нике отключено! 👍'
                await message.reply(text=text, disable_web_page_preview=True)
            if arg[1].lower() == 'вкл':
                user.edit('clan_teg', True)
                text = f'{user.link}, теперь Ваш клан отображается в нике!'
                await message.reply(text=text, disable_web_page_preview=True)
        else:
            return await message.reply('❌ Ошибка. Используйте помощь чтобы узнать команды!')


@flags.throttling_key('default')
async def info_callback_user(callback_query: CallbackQuery):
    call = callback_query.data.split('claninfo_')[1]
    action, user2, user = call.split(':')
    try:
        clanuser = Clanuser(user_id=user)
    except:
        return await callback_query.message.edit_text(
            text='❕ вы не состоите в клане!')
    clan = Clan(clan_id=clanuser.id_clan)
    if int(user) == callback_query.from_user.id:
        if clanuser is None:
            return await callback_query.message.edit_text('❌ У вас нет клана :(')
        try:
            clanuser2 = Clanuser(user_id=user2)
        except:
            return await callback_query.message.edit_text(
                text='❕ Он не состоит в вашем клане!')

        if clanuser.id_clan != clanuser2.id_clan and clanuser.id != user2:
            return await callback_query.message.edit_text(
                text='❕ Он не состоит в вашем клане!')

        if clanuser.status <= 0:
            return await callback_query.message.edit_text('❌ Низкий ранг!')
        if clan.owner == user2:
            return await callback_query.message.edit_text('❌ Нельзя изменить статус главы!')
        if action == 'k':
            clanuser2.dellclan()
            clan.edit('members', clan.members - 1)
            return await callback_query.message.edit_text(text='✅ Вы успешно кикнули игрока!')
        if action == 'up':
            if clanuser2.status + 1 == 2:
                return await callback_query.message.edit_text(text='❕ У пользователя макс. ранг!')
            clanuser2.edit('status', clanuser2.status + 1)
            user = User(id=user2)
            return await callback_query.message.edit_text(text=f'👤 Игрок: {user.link}\n'
                                                               f'👑 Ранг: {status_clan[clanuser2.status]["name"]}\n'
                                                               f'🏆 Рейтинг: {clanuser2.rating}🏆\n'
                                                               f'📅 Дата рег: {clanuser2.reg_date}\n'
                                                          , reply_markup=info_clan(user2, clanuser.id,
                                                                                   clanuser2.status).adjust(
                    1).as_markup(), disable_web_page_preview=True)
        if action == 'dow':
            if clanuser2.status - 1 < 0:
                return await callback_query.message.edit_text(text='❕ У пользователя мин. ранг!')
            clanuser2.edit('status', clanuser2.status - 1)
            user = User(id=user2)
            return await callback_query.message.edit_text(text=f'👤 Игрок: {user.link}\n'
                                                               f'👑 Ранг: {status_clan[clanuser2.status]["name"]}\n'
                                                               f'🏆 Рейтинг: {clanuser2.rating}🏆\n'
                                                               f'📅 Дата рег: {clanuser2.reg_date}\n'
                                                          , reply_markup=info_clan(user2, clanuser.id,
                                                                                   clanuser2.status).adjust(
                    1).as_markup(), disable_web_page_preview=True)

    else:
        await callback_query.answer("❌ Не трожь не твое!", show_alert=False)


@flags.throttling_key('default')
async def info_callback_invate(callback_query: CallbackQuery):
    call = callback_query.data.split('invite_')[1]
    user_in, clan_id, owner = call.split(' ')
    if int(owner) == callback_query.from_user.id:
        user = User(id=user_in)
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text=f'❌ Отклонить', callback_data=f"clan_d:{user_in}:{clan_id}:{owner}"))
        keyboard.add(InlineKeyboardButton(text=f'✅ Принять', callback_data=f"clan_a:{user_in}:{clan_id}:{owner}"))
        keyboard.add(InlineKeyboardButton(text=f'🔙 Назад', callback_data=f"clan_b:{user_in}:{clan_id}:{owner}"))

        return await callback_query.message.edit_text(f'❕ Игрок {user.link}',
                                                      reply_markup=keyboard.adjust(1).as_markup(),
                                                      disable_web_page_preview=True)
    else:
        await callback_query.answer("❌ Не трожь не твое!", show_alert=False)


@flags.throttling_key('default')
async def invate_solution(callback_query: CallbackQuery):
    call = callback_query.data.split('clan_')[1]
    action, user1, clan_id, owner = call.split(':')
    clan = Clan(clan_id=int(clan_id))
    user = User(id=user1)
    if action == 'd' and callback_query.from_user.id == int(owner):
        clan.invites = list(clan.invites)
        if clan.invites[0] == '':
            return await callback_query.message.edit_text('❕ На данный момент нету заявок!')
        clan.dell_invites(user1)
        return await callback_query.message.edit_text(f'Игрок {user.link} отказ', disable_web_page_preview=True)
    elif action == 'a' and callback_query.from_user.id == int(owner):
        clan.invites = list(clan.invites)
        if clan.invites[0] == '':
            return await callback_query.message.edit_text('❕ На данный момент нету заявок!')
        clan.dell_invites(user1)
        Clanuser.create2(user1, clan.id)
        clan.edit('members', clan.members + 1)
        return await callback_query.message.edit_text(f'❕ Игрок {user.link} принят', disable_web_page_preview=True)
    elif action == 'b' and callback_query.from_user.id == int(owner):
        clan.invites = list(clan.invites)
        if clan.invites[0] != '':
            text = '🛃 Заявки:\n'
            keyboard = InlineKeyboardBuilder()
            for i in clan.invites:
                user = User(id=int(i))
                text += f'👤 Пользователь: {user.link}\n'
                button = InlineKeyboardButton(text=f'{user.first_name}',
                                              callback_data=f"invite_{int(i)} {clan.id} {clan.owner}")
                keyboard.add(button)
            return await callback_query.message.edit_text(text=text, reply_markup=keyboard.adjust(1).as_markup(),
                                                          disable_web_page_preview=True)
        else:
            return await callback_query.message.edit_text('❕ На данный момент нету заявок!')
    else:
        await callback_query.answer("❌ Не трожь не твое!", show_alert=False)


@flags.throttling_key('default')
async def mamber_handler(callback_query: CallbackQuery):
    try:
        clanuser = Clanuser(user_id=callback_query.from_user.id)
    except:
        clanuser = None
    if clanuser is None:
        return await callback_query.answer('❌ У вас нет клана :(')

    call = callback_query.data.split('members_')[1]
    clan = Clan(clan_id=call[0])
    user = User(id=callback_query.from_user.id)
    user_ids = sql.execute(query=f'SELECT id FROM clan_users WHERE id_clan={clan.id}', commit=False, fetch=True)
    text = f"{user.link}, участники клана [{clan.name}]\n"
    for user in user_ids:
        user1 = User(id=user[0])
        clanuser = Clanuser(user_id=user[0])
        if clanuser.status == 0:
            text += f'[👤]{user1.link}(<code>{user1.id}</code>)— 🏆 {clanuser.rating}\n'
        if clanuser.status == 1:
            text += f'[💎]{user1.link}(<code>{user1.id}</code>)— 🏆 {clanuser.rating}\n'
        if clanuser.status == 2:
            text += f'[👑]{user1.link}(<code>{user1.id}</code>)— 🏆 {clanuser.rating}\n'
    return await callback_query.message.reply(text=text, disable_web_page_preview=True)
