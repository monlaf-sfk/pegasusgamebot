import random
import re

from contextlib import suppress

from aiogram import flags, Bot
from aiogram.client import bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.utils.keyboard import InlineKeyboardBuilder

from filters.users import flood_handler
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery

from keyboard.clans import member_kb, info_clan

from config import bot_name
from keyboard.main import settings2_switch_kb, settings4_switch_kb
from utils.clan.clan import Clanuser, Clan, status_clan, level_clan
from utils.clan.clanwar import ClanWar, ClanWarFind
from utils.logs import writelog
from utils.main.cash import get_cash, to_str
from utils.main.db import sql
from utils.main.users import User, Settings
from utils.weapons.swords import ArmoryInv


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
        if len(arg) != 0 and arg[0].lower() in ['создать', 'основать']:
            if clanuser:
                return await message.reply(f'❌ {user.link}, У вас уже есть клан... Предатель найден!',
                                           disable_web_page_preview=True)
            price = 200
            armory_inv = ArmoryInv(message.from_user.id)
            if price > armory_inv.tokens:
                return await message.reply(f'❌ Недостаточно 💠 tokens для покупки!\n'
                                           f'▶ Нужно : {price} 💠', show_alert=True)
            try:
                name = re.sub('''[@"'%<>💎👨‍🔬🌟⚡👮‍♂➪👾🥲⛏😎👑💖🐟🍆😈🏿🐥👶🏿🇷🇺🇺🇦]''', '', arg[1])
            except:
                return await message.reply(f'❌ {user.link}, Используйте: <code>Клан создать [название]</code>',
                                           disable_web_page_preview=True)
            if len(name) < 4 or len(name) > 16:
                return await message.reply(f'❌ {user.link}, Длина больше 16 или меньше 4. Запрещены символы.',
                                           disable_web_page_preview=True)
            names = sql.execute("SELECT name FROM Clans", fetch=True)

            if name in str(names):
                return await message.reply(
                    f'{user.link}, клан с названием «{name}» уже существует\n'
                    '▶️ Придумайте другое название', disable_web_page_preview=True)
            armory_inv.editmany(tokens=armory_inv.tokens - price)
            Clan.create(message.from_user.id, name)
            clan = Clan(owner=message.from_user.id)
            Clanuser.create(message.from_user.id, clan.id, 2)
            await message.reply(f'✅ {user.link}, Вы успешно создали клан {name}', disable_web_page_preview=True)

            return
        elif len(arg) != 0 and arg[0].lower() in ['вступить', 'войти']:
            try:
                clan = Clan(clan_id=arg[1])
            except:
                return await message.reply(f'❌ {user.link}, Не найден клан с таким айди!',
                                           disable_web_page_preview=True)
            if level_clan[clan.level]["members"] < clan.members + 1:
                return await message.reply(f'❌ {user.link}, Клан  переполнен!',
                                           disable_web_page_preview=True)
            if clan.owner == None and clan.members == 0:
                Clanuser.create(message.from_user.id, clan.id, 2)
                clan.edit('members', clan.members + 1)
                clan.edit('owner', message.from_user.id)
                return await message.reply(f'✅ {user.link}, Вы вступили в клан {clan.name}\n'
                                           f'Прошлый владелц струсил и убежал и теперь ты стал главой клана!',
                                           disable_web_page_preview=True)
            if clan.type == 0:
                Clanuser.create(message.from_user.id, clan.id, 0)
                clan.edit('members', clan.members + 1)
                return await message.reply(f'✅ {user.link}, Вы вступили в клан {clan.name}',
                                           disable_web_page_preview=True)
            if clan.type == 1:
                return await message.reply(f'❌ {user.link}, Клан {clan.name} закрыт!', disable_web_page_preview=True)
            if clan.type == 2:
                clan.add_invites(message.from_user.id)
                await message.reply(f'Заявка в клан отправлена!!')
                try:
                    await bot.send_message(clan.owner, f'Вам поступила заявка в клан!')
                except:
                    pass
                return
        elif len(arg) != 0 and arg[0].lower() in ['тег']:
            if len(arg) <= 1:
                return await message.reply(f'❌ {user.link},  Используйте Клан тег [вкл\выкл]!',
                                           disable_web_page_preview=True,
                                           reply_markup=settings4_switch_kb)
            settings = Settings(user.id)
            if arg[1].lower() == 'выкл':
                settings.edit('nick_clanteg', False)
                text = f'{user.link}, отображение клана в нике отключено! 👍'
                await message.reply(text=text, disable_web_page_preview=True,
                                    reply_markup=settings4_switch_kb)
            if arg[1].lower() == 'вкл':
                settings.edit('nick_clanteg', True)
                text = f'{user.link}, теперь Ваш клан отображается в нике!'
                await message.reply(text=text, disable_web_page_preview=True,
                                    reply_markup=settings4_switch_kb)
            return
        if clanuser is None:
            return await message.reply(f'❌ {user.link}, У вас нет клана :(', disable_web_page_preview=True)
        if len(arg) == 0 or arg[0].lower() in ['мой', 'моя', 'моё']:
            clan = Clan(clan_id=clanuser.clan_id)
            text_clanwar = ''
            games = 0
            try:
                clanwar = ClanWar(clan_id=clan.id)
                members_mine = sql.select_data(table='WarParticipants', title='clan_id', name=clan.id)
                members_enemy = sql.select_data(table='WarParticipants', title='clan_id', name=
                clanwar.id_first if clanwar.id_first != clan.id else clanwar.id_second)
                if members_mine:
                    for member in members_mine:
                        games += member[4]
                if clanwar.prepare:
                    text_clanwar = \
                        f'⚔️ Война против «{clanwar.name_first if clanwar.name_first != clan.name else clanwar.name_second}»(👥{len(members_enemy if members_enemy else [])})\n' \
                        f'  🗡 Текущая стадия: отбор участников 👤\n' \
                        f'  🎮 Игр: {games}\n'
                else:
                    text_clanwar = \
                        f'⚔️ Война против «{clanwar.name_first if clanwar.name_first != clan.name else clanwar.name_second}»(👥{len(members_enemy if members_enemy else [])})\n' \
                        f'  🗡 Текущая стадия: собирание звезд ⭐️\n' \
                        f'  🎮 Игр: {games}\n'
            except:
                try:
                    find = ClanWarFind(clan_id=clan.id)
                except:
                    find = None
                if find:
                    text_clanwar = \
                        f'⚔️ Идёт поиск противника...\n' \
                        f'  🗡 Текущая стадия: подбор противника️\n' \
                        f'  🎮 Игр: {games}\n'

            text = f'{user.link} ,\nинформация о Вашем клане:\n' \
                   f'✏️ Название: {clan.name}\n' \
                   f'🛡 Уровень: {level_clan[clan.level]["symbol"]}\n' \
                   f'🔎 ID клана: {clan.id}\n' \
                   f'👑 Ваш ранг: {status_clan[clanuser.status]["name"]}\n' \
                   f'🔒 Тип: {"Закрыт" if clan.type == 1 else "Открыт" if clan.type == 0 else "По Приглашению"}\n' \
                   f'♨ Префикс: {clan.prefix if clan.prefix != "" else "Нету"}\n\n' \
                   f'🏆 Рейтинг: {clan.rating}\n' \
                   f'💰 В казне: {to_str(clan.kazna)}\n\n' \
                   f'📋 Описание: {clan.description}\n\n' \
                   f'{text_clanwar}\n' \
                   f'💪 БМ: {clan.power}\n' \
                   f'🥇 Побед: {clan.win}\n' \
                   f'💀 Проигрышей: {clan.lose}\n\n' \
                   f' 👥 Участники ({clan.members}/{level_clan[clan.level]["members"]})\n'
            # f'➖➖➖➖➖➖➖➖\n'f'💵 Ограбление: \n'\
            return await message.reply(text=text, reply_markup=member_kb(clanuser.clan_id).as_markup(),
                                       disable_web_page_preview=True)
        elif arg[0].lower() in ['выйти', 'удалить', 'покинуть']:
            try:
                clanwar = ClanWar(clan_id=clanuser.id)
            except:
                clanwar = None
            if clanwar:
                return await message.reply(f'❌ {user.link}, Вы не можете выйти пока идет Клановая война!',
                                           disable_web_page_preview=True)
            clan = Clan(clan_id=clanuser.clan_id)
            if clanuser.status == 2:
                clanuser.dellclan()
                clan.edit('members', clan.members - 1)
                clan.edit('owner', None)
                if clan.members > 0:
                    user_ids = sql.execute(query=f'SELECT user_id FROM ClanUsers WHERE clan_id={clan.id}', commit=False,
                                           fetch=True)
                    list_user = []
                    for user_id in user_ids:
                        list_user.append(f"{user_id[0]}")

                    random_index = random.randrange(len(list_user))
                    new_id = int(list_user[random_index])
                    clan.edit('owner', new_id)
                    clanuser = Clanuser(user_id=new_id)
                    clanuser.edit('status', 2)

            else:
                clanuser.dellclan()
                clan.edit('members', clan.members - 1)

            return await message.reply(f'✅ {user.link}, Вы успешно покинули', disable_web_page_preview=True)

        elif arg[0].lower() in ['снять', 'вывести']:
            clan = Clan(clan_id=clanuser.clan_id)
            summ = 0
            try:
                summ = get_cash(arg[1])
            except:
                pass

            if summ <= 0:
                return await message.reply(f'❌ {user.link}, Минимум $1', disable_web_page_preview=True)

            elif summ > clan.kazna:
                return await message.reply(f'❌ {user.link}, Недостаточно средств на счету клана!',
                                           disable_web_page_preview=True)
            if clanuser.status <= 0:
                return await message.reply(f'❌ {user.link}, Низкий ранг!', disable_web_page_preview=True)
            sql.executescript(f'UPDATE users SET balance = balance + {summ} WHERE id = {message.from_user.id};\n'
                              f'UPDATE Clans SET kazna = kazna - {summ} WHERE id = {clanuser.clan_id}',
                              True, False)

            await message.reply(f'✅ Вы успешно сняли {to_str(summ)} с бюджета клана!')
            await writelog(message.from_user.id, f'Снятие {to_str(summ)} с бюджета клана')
            return
        elif arg[0].lower() in ['положить', 'вложить', 'пополнить']:
            clan = Clan(clan_id=clanuser.clan_id)
            summ = 0
            try:
                summ = get_cash(arg[1])
            except:
                pass
            if user.payban:
                return await message.reply(f'❌ {user.link},На ваш аккаунт наложено ограничение на переводы !',
                                           disable_web_page_preview=True)
            if summ <= 0:
                return await message.reply(f'❌ {user.link}, Минимум $1', disable_web_page_preview=True)

            elif summ > user.balance:
                return await message.reply(f'❌ {user.link}, Недостаточно средств на руках!',
                                           disable_web_page_preview=True)

            if clan.kazna + summ > level_clan[clan.level]['kazna']:
                return await message.reply(f'❌ {user.link}, В казне нету места для вклада',
                                           disable_web_page_preview=True)
            sql.executescript(f'UPDATE users SET balance = balance - {summ} WHERE id = {message.from_user.id};\n'
                              f'UPDATE Clans SET kazna = kazna + {summ} WHERE id = {clanuser.clan_id}',
                              True, False)

            await message.reply(f'✅ Вы успешно пополнили бюджет клана на +{to_str(summ)}')
            await writelog(message.from_user.id, f'Пополнение {to_str(summ)} в бюджет клана')
            return


        elif arg[0].lower() in ['улучшить']:
            clan = Clan(clan_id=clanuser.clan_id)
            if clanuser.status <= 1:
                return await message.reply(f'❌ {user.link}, у вас низкий ранг для этого действия!',
                                           disable_web_page_preview=True)
            if clan.level == 3:
                return await message.reply(
                    f'{user.link}, Ваш клан максимально улучшен ☺', disable_web_page_preview=True)
            price = 125_500_000 * (clan.level + 1)
            if user.balance < price:
                return await message.reply(
                    f'💲 Недостаточно денег на руках для улучшения клана. Нужно: {to_str(price)}')

            query = f'UPDATE users SET balance = balance - {price} WHERE id = {message.from_user.id};\n' \
                    f'UPDATE Clans SET level = level + 1 WHERE id = {clanuser.clan_id};'

            sql.executescript(query=query, commit=True, fetch=False)
            text = f'✅ {user.link}, клан улучшен до {level_clan[clan.level + 1]["symbol"]} уровня\n' \
                   f'👥 Максимальное количество участников: {level_clan[clan.level + 1]["members"]}\n' \
                   f'💰 Максимальная сумма в банке клана: {to_str(level_clan[clan.level + 1]["kazna"])}\n' \
                   f'📝 Увеличена максимальная длина названия\n'
            if clan.level + 1 == 3:
                text += '\n🔥 Максимальный уровень клана!'
            else:
                text += f'\n⏫ Следующее улучшение - {to_str(125_500_000 * (clan.level + 2))}'
            return await message.reply(text,
                                       disable_web_page_preview=True)
        elif arg[0].lower() in ['закрыть', 'открыть', 'пригл']:
            clan = Clan(clan_id=clanuser.clan_id)

            if clanuser.status <= 1:
                return await message.reply(f'❌ {user.link},у вас низкий ранг для этого действия!',
                                           disable_web_page_preview=True)
            if arg[0].lower() in ['закрыть']:
                clan.edit('type', 1)
                return await message.reply(f'✅ {user.link}, Клан закрыт', disable_web_page_preview=True)
            if arg[0].lower() in ['открыть']:
                clan.edit('type', 0)
                return await message.reply(f'✅ {user.link}, Клан открыт', disable_web_page_preview=True)
            if arg[0].lower() in ['пригл']:
                clan.edit('type', 2)
                return await message.reply(f'✅ {user.link}, Вступление по приглашению', disable_web_page_preview=True)

        elif arg[0].lower() in ['заявки']:
            clan = Clan(clan_id=clanuser.clan_id)
            if clanuser.status <= 0:
                return await message.reply(f'❌ {user.link},у вас низкий ранг для этого действия!',
                                           disable_web_page_preview=True)
            clan.invites = list(clan.invites)
            if clan.invites[0] != '':
                text = '🛃 Заявки:\n'
                keyboard = InlineKeyboardBuilder()
                for i in clan.invites:
                    user = User(id=int(i))
                    text += f'👤 Пользователь: {user.link}\n'
                    button = InlineKeyboardButton(text=f'{user.first_name}',
                                                  callback_data=f"invite_{int(i)} {clan.id} {clanuser.user_id}")
                    keyboard.add(button)
                return await message.reply(text=text, reply_markup=keyboard.adjust(1).as_markup(),
                                           disable_web_page_preview=True)
            else:
                return await message.reply(f'❌ {user.link}, На данный момент нету заявок!',
                                           disable_web_page_preview=True)
        elif arg[0].lower() in ['повысить']:
            if clanuser.status <= 1:
                return await message.reply(f'❌ {user.link},у вас низкий ранг для этого действия!',
                                           disable_web_page_preview=True)
            try:
                if arg[1].isdigit():
                    id = int(arg[1])
                    try:
                        clanuser2 = Clanuser(user_id=id)
                    except:
                        return await message.reply(
                            text=f'❕ {user.link}, Он не состоит в вашем клане!', disable_web_page_preview=True)
                    if clanuser2.status + 1 == 2:
                        return await message.reply(text=f'❕ {user.link}, У пользователя макс. ранг!',
                                                   disable_web_page_preview=True)

                    if clanuser.clan_id != clanuser2.clan_id and clanuser.user_id != id:
                        return await message.reply(
                            text=f'❕ {user.link}, Он не состоит в вашем клане!', disable_web_page_preview=True)
                    clanuser2.edit('status', clanuser2.status + 1)
                    return await message.reply(text=f'✅ {user.link}, Вы успешно повысили игрока!',
                                               disable_web_page_preview=True)
                else:

                    return await message.reply(
                        text=f'🆔 {user.link}, Введите id пользователя которого хотите повысить\понизить!\n'
                             '➖ Клан повысить\понизить id', disable_web_page_preview=True)
            except Exception as e:
                print(e)
                return await message.reply(
                    text=f'🆔 {user.link}, Введите id пользователя которого хотите повысить\понизить!\n'
                         '➖ Клан повысить\понизить id', disable_web_page_preview=True)
        elif arg[0].lower() in ['понизить']:
            if clanuser.status <= 1:
                return await message.reply(f'❌ {user.link},у вас низкий ранг для этого действия!',
                                           disable_web_page_preview=True)
            try:
                if arg[1].isdigit():
                    id = arg[1]
                    try:
                        clanuser2 = Clanuser(user_id=id)
                    except:
                        return await message.reply(
                            text=f'❕ {user.link}, Он не состоит в вашем клане!', disable_web_page_preview=True)
                    if clanuser2.status - 1 < 0:
                        return await message.reply(text=f'❕ {user.link}, У пользователя мин. ранг!',
                                                   disable_web_page_preview=True)

                    if clanuser.clan_id != clanuser2.clan_id and clanuser.user_id != id:
                        return await message.reply(
                            text=f'❕ {user.link}, Он не состоит в вашем клане!', disable_web_page_preview=True)
                    clanuser2.edit('status', clanuser2.status - 1)
                    return await message.reply(text=f'✅ {user.link}, Вы успешно понизили игрока!',
                                               disable_web_page_preview=True)
                else:
                    return await message.reply(
                        text=f'🆔 {user.link}, Введите id пользователя которого хотите повысить\понизить!\n'
                             '➖ Клан повысить\понизить id', disable_web_page_preview=True)
            except:
                return await message.reply(
                    text=f'🆔 {user.link}, Введите id пользователя которого хотите повысить\понизить!\n'
                         '➖ Клан повысить\понизить id', disable_web_page_preview=True)

        elif arg[0].lower() in ['кик']:
            if clanuser.status <= 0:
                return await message.reply(f'❌ {user.link},у вас низкий ранг для этого действия!',
                                           disable_web_page_preview=True)

            try:
                clanwar = ClanWar(clan_id=clanuser.id)
            except:
                clanwar = None
            if clanwar:
                return await message.reply(f'❌ {user.link}, Вы не можете кикать пока идет Клановая война!',
                                           disable_web_page_preview=True)
            try:
                clan = Clan(clan_id=clanuser.clan_id)
                if arg[1].isdigit():
                    id = arg[1]
                    try:
                        clanuser2 = Clanuser(user_id=id)
                    except:
                        return await message.reply(
                            text=f'❕ {user.link}, Он не состоит в вашем клане!', disable_web_page_preview=True)

                    if clanuser.clan_id != clanuser2.clan_id and clanuser.user_id != id:
                        return await message.reply(
                            text=f'❕ {user.link}, Он не состоит в вашем клане!', disable_web_page_preview=True)
                    clanuser2.dellclan()
                    clan.edit('members', clan.members - 1)
                    return await message.reply(text=f'✅ {user.link}, Вы успешно кикнули игрока!',
                                               disable_web_page_preview=True)
                else:
                    return await message.reply(
                        text=f'🆔 {user.link}, Введите id пользователя которого хотите кикнуть!\n'
                             '➖ Клан кикнуть id', disable_web_page_preview=True)
            except:
                return await message.reply(text=f'🆔 {user.link}, Введите id пользователя которого хотите кикнуть!\n'
                                                '➖ Клан кикнуть id', disable_web_page_preview=True)
        elif arg[0].lower() in ['участники']:
            clan = Clan(clan_id=clanuser.clan_id)
            user = User(id=message.from_user.id)
            user_ids = sql.execute(query=f'SELECT user_id FROM ClanUsers WHERE clan_id={clan.id}', commit=False,
                                   fetch=True)
            text = f"{user.link}, участники клана [{clan.name}]\n"
            for user in user_ids:
                user1 = User(id=user[0])
                clanuser = Clanuser(user_id=user[0])
                if clanuser.status == 0:
                    text += f'[👤]{user1.link}(<code>{user1.id}</code>)— 🏆 {clanuser.rating}\n' \
                            f'💪 БМ: {clanuser.power}\n'
                if clanuser.status == 1:
                    text += f'[💎]{user1.link}(<code>{user1.id}</code>)— 🏆 {clanuser.rating}\n' \
                            f'💪 БМ: {clanuser.power}\n'
                if clanuser.status == 2:
                    text += f'[👑]{user1.link}(<code>{user1.id}</code>)— 🏆 {clanuser.rating}\n' \
                            f'💪 БМ: {clanuser.power}\n'
            return await message.reply(text=text, disable_web_page_preview=True)

        elif arg[0].lower() in ['инфо']:
            if clanuser.status <= 0:
                return await message.reply(f'❌ {user.link},у вас низкий ранг для этого действия!',
                                           disable_web_page_preview=True)
            try:
                if arg[1].isdigit():
                    id = int(arg[1])
                    try:
                        clanuser2 = Clanuser(user_id=id)
                    except:
                        return await message.reply(
                            text=f'❕ {user.link}, Он не состоит в вашем клане!', disable_web_page_preview=True)

                    if clanuser.clan_id != clanuser2.clan_id and clanuser.user_id != id:
                        return await message.reply(
                            text=f'❕ {user.link}, Он не состоит в вашем клане!', disable_web_page_preview=True)
                    user = User(id=id)
                    clan = Clan(clan_id=clanuser.clan_id)
                    if clan.owner == id:
                        return await message.reply(text=f'👤 Игрок: {user.link}\n'
                                                        f'👑 Ранг: {status_clan[clanuser2.status]["name"]}\n'
                                                        f'🏆 Рейтинг: {clanuser2.rating}🏆\n' \
                                                        f'💪 БМ: {clanuser.power}\n'
                                                        f'📅 Дата рег: {clanuser2.reg_date}\n')
                    return await message.reply(text=f'👤 Игрок: {user.link}\n'
                                                    f'👑 Ранг: {status_clan[clanuser2.status]["name"]}\n'
                                                    f'🏆 Рейтинг: {clanuser2.rating}🏆\n' \
                                                    f'💪 БМ: {clanuser.power}\n'
                                                    f'📅 Дата рег: {clanuser2.reg_date}\n'
                                               , reply_markup=info_clan(id, clanuser.user_id, clanuser2.status).adjust(
                            1).as_markup(), disable_web_page_preview=True)
                else:
                    return await message.reply(text=f'🆔 {user.link}, Введите id игрока !\n'
                                                    '➖ Клан инфо id', disable_web_page_preview=True)
            except:
                return await message.reply(text=f'🆔 {user.link}, Введите id игрока !\n'
                                                '➖ Клан инфо id', disable_web_page_preview=True)

        elif arg[0].lower() in ['преф', 'префикс']:
            clan = Clan(clan_id=clanuser.clan_id)
            if clanuser.status <= 0:
                return await message.reply(f'❌ {user.link},у вас низкий ранг для этого действия!',
                                           disable_web_page_preview=True)
            try:
                name = re.sub('''[@"'%<>💎👨‍🔬🌟⚡👮‍♂➪👾🥲⛏😎👑💖🐟🍆😈🏿🐥👶🏿🇷🇺🇺🇦]''', '', arg[1])
            except:
                return await message.reply(f'❌ {user.link}, Используйте: <code>Клан преф [название]</code>',
                                           disable_web_page_preview=True)
            if len(name) > 4 or len(name) < 3:
                return await message.reply(f'''❌ {user.link}, Длина 4-3. Запрещеные символы.''',
                                           disable_web_page_preview=True)
            prefixes = sql.execute("SELECT prefix FROM Clans", fetch=True)

            if f"[{name.upper()}]" in str(prefixes):
                return await message.reply(
                    f'''❌ {user.link}, Данный префикс уже занят''', disable_web_page_preview=True)
            clan.edit('prefix', f"[{name.upper()}]")
            return await message.reply(
                f'❕ {user.link}, Успешно сменили префикс на: {name.upper()}', disable_web_page_preview=True)
        elif arg[0].lower() in ['описание']:
            clan = Clan(clan_id=clanuser.clan_id)
            if clanuser.status <= 0:
                return await message.reply(f'❌ {user.link},у вас низкий ранг для этого действия!',
                                           disable_web_page_preview=True)

            try:
                description = re.sub('''[@"'%<>]''', '', ' '.join(arg[1:]))
            except:
                return await message.reply(f'❌ {user.link}, Используйте: <code>Клан описание [текст]</code>',
                                           disable_web_page_preview=True)
            if len(description) > level_clan[clan.level]['description'] or len(description) < 0:
                return await message.reply(
                    f'''❌ {user.link}, Длина {level_clan[clan.level]['description']}-0. Запрещеные символы.''',
                    disable_web_page_preview=True)

            clan.edit('description', description)
            return await message.reply(
                f'❕ {user.link}, Успешно сменили описание клана', disable_web_page_preview=True)

        else:
            return await message.reply(f'❌ {user.link},  Используйте помощь чтобы узнать команды!',
                                       disable_web_page_preview=True)


@flags.throttling_key('default')
async def info_callback_user(callback_query: CallbackQuery):
    call = callback_query.data.split('claninfo_')[1]
    action, user2, user_id = call.split(':')
    try:
        clanuser = Clanuser(user_id=user_id)
    except:
        return await callback_query.message.edit_text(
            text=f'❕ вы не состоите в клане!', disable_web_page_preview=True)
    clan = Clan(clan_id=clanuser.clan_id)
    if int(user_id) == callback_query.from_user.id:
        if clanuser is None:
            return await callback_query.message.edit_text(f'❌ У вас нет клана :(', disable_web_page_preview=True)
        try:
            clanuser2 = Clanuser(user_id=user2)
        except:
            return await callback_query.message.edit_text(
                text=f'❕ Он не состоит в вашем клане!', disable_web_page_preview=True)

        if clanuser.clan_id != clanuser2.clan_id and clanuser.user_id != user2:
            return await callback_query.message.edit_text(
                text=f'❕ Он не состоит в вашем клане!', disable_web_page_preview=True)

        if clanuser.status <= 0:
            return await callback_query.message.edit_text(f'❌ Низкий ранг!', disable_web_page_preview=True)
        if clan.owner == user2:
            return await callback_query.message.edit_text(f'❌ Нельзя изменить статус главы!',
                                                          disable_web_page_preview=True)
        if action == 'k':
            try:
                clanwar = ClanWar(clan_id=clanuser.id)
            except:
                clanwar = None
            if clanwar:
                return await callback_query.message.edit_text(f'❌ Вы не можете кикать пока идет Клановая война!',
                                                              disable_web_page_preview=True)
            clanuser2.dellclan()
            clan.edit('members', clan.members - 1)
            return await callback_query.message.edit_text(text=f'✅ Вы успешно кикнули игрока!',
                                                          disable_web_page_preview=True)
        if action == 'up':
            if clanuser2.status + 1 == 2:
                return await callback_query.message.edit_text(text=f'❕ У пользователя макс. ранг!',
                                                              disable_web_page_preview=True)
            clanuser2.edit('status', clanuser2.status + 1)
            user = User(id=user2)
            return await callback_query.message.edit_text(text=f'👤 Игрок: {user.link}\n'
                                                               f'👑 Ранг: {status_clan[clanuser2.status]["name"]}\n'
                                                               f'🏆 Рейтинг: {clanuser2.rating}🏆\n' \
                                                               f'💪 БМ: {clanuser.power}\n'
                                                               f'📅 Дата рег: {clanuser2.reg_date}\n'
                                                          , reply_markup=info_clan(user2, clanuser.user_id,
                                                                                   clanuser2.status).adjust(
                    1).as_markup(), disable_web_page_preview=True)
        if action == 'dow':
            if clanuser2.status - 1 < 0:
                return await callback_query.message.edit_text(text='❕ У пользователя мин. ранг!',
                                                              disable_web_page_preview=True)
            clanuser2.edit('status', clanuser2.status - 1)
            user = User(id=user2)
            return await callback_query.message.edit_text(text=f'👤 Игрок: {user.link}\n'
                                                               f'👑 Ранг: {status_clan[clanuser2.status]["name"]}\n'
                                                               f'🏆 Рейтинг: {clanuser2.rating}🏆\n' \
                                                               f'💪 БМ: {clanuser.power}\n'
                                                               f'📅 Дата рег: {clanuser2.reg_date}\n'
                                                          , reply_markup=info_clan(user2, clanuser.user_id,
                                                                                   clanuser2.status).adjust(
                    1).as_markup(), disable_web_page_preview=True)

    else:
        await callback_query.answer("❌ Не трожь не твое!", show_alert=False, cache_time=3)


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
        await callback_query.answer("❌ Не трожь не твое!", show_alert=False, cache_time=3)


@flags.throttling_key('default')
async def invate_solution(callback_query: CallbackQuery, bot: Bot):
    call = callback_query.data.split('clan_')[1]
    action, user1, clan_id, owner = call.split(':')
    clan = Clan(clan_id=int(clan_id))
    user = User(id=user1)
    if action == 'd' and callback_query.from_user.id == int(owner):
        clan.invites = list(clan.invites)
        if clan.invites[0] == '':
            return await callback_query.message.edit_text('❕ На данный момент нету заявок!',
                                                          disable_web_page_preview=True)
        clan.dell_invites(user1)
        settings = Settings(user.id)
        if settings.clan_notifies:
            with suppress(TelegramBadRequest, TelegramForbiddenError):
                await bot.send_message(user.id, '[КЛАН]\n'
                                                f'▶ Ваша заявка в клан «{clan.name}» отклонена')
        return await callback_query.message.edit_text(f'Игрок {user.link} отказ', disable_web_page_preview=True)
    elif action == 'a' and callback_query.from_user.id == int(owner):

        clan.invites = list(clan.invites)
        if clan.invites[0] == '':
            return await callback_query.message.edit_text('❕ На данный момент нету заявок!',
                                                          disable_web_page_preview=True)
        if level_clan[clan.level]["members"] < clan.members + 1:
            return await callback_query.message.edit_text(f'❌  Клан  переполнен!',
                                                          disable_web_page_preview=True)
        try:
            clan_user = Clanuser(user_id=user1)

        except:
            clan_user = None
        if clan_user:
            return await callback_query.message.edit_text(
                text=f'❕ Он уже состоит в клане!', disable_web_page_preview=True)
        clan.dell_invites(user1)
        Clanuser.create(user1, clan.id, 0)
        clan.edit('members', clan.members + 1)
        settings = Settings(user.id)
        if settings.clan_notifies:
            with suppress(TelegramBadRequest, TelegramForbiddenError):
                await bot.send_message(user.id, '[КЛАН]\n'
                                                f'▶ Ваша заявка в клан «{clan.name}» одобрена'
                                                f'▶ Для просмотра информации о клане введите «Клан»')
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
        await callback_query.answer("❌ Не трожь не твое!", show_alert=False, cache_time=3)


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
    user_ids = sql.execute(query=f'SELECT user_id FROM ClanUsers WHERE clan_id={clan.id}', commit=False, fetch=True)
    text = f"{user.link}, участники клана [{clan.name}]\n"
    for user in user_ids:
        user1 = User(id=user[0])
        clanuser = Clanuser(user_id=user[0])
        if clanuser.status == 0:
            text += f'[👤]{user1.link}(<code>{user1.id}</code>)— 🏆 {clanuser.rating}\n' \
                    f'💪 БМ: {clanuser.power}\n'
        if clanuser.status == 1:
            text += f'[💎]{user1.link}(<code>{user1.id}</code>)— 🏆 {clanuser.rating}\n' \
                    f'💪 БМ: {clanuser.power}\n'
        if clanuser.status == 2:
            text += f'[👑]{user1.link}(<code>{user1.id}</code>)— 🏆 {clanuser.rating}\n' \
                    f'💪 БМ: {clanuser.power}\n'
    return await callback_query.message.reply(text=text, disable_web_page_preview=True)
