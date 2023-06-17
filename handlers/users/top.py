from aiogram import flags
from aiogram.types import Message, CallbackQuery

from config import bot_name
from keyboard.main import top_kb_func, top_back_func
from utils.clan.clan import Clan, Clanuser
from utils.main.cash import transform, to_str2
from utils.main.db import sql

from utils.main.users import User

numbers_emoji = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']


@flags.throttling_key('default')
async def top_handler(message: Message):
    text = '🔝 10 Пользователей по ({}):\n<i>📢 Всего пользователей: {}</i>\n\n'
    arg = ' '.join(
        message.text.split()[1:] if not bot_name.lower() in message.text.split()[0].lower() else message.text.split()[
                                                                                                 2:])
    if len(arg) == 0 or 'общ' in arg.lower() or 'все' in arg.lower() or 'всё' in arg.lower():

        top_users = sql.execute(
            'SELECT id, first_name, name, username, deposit+bank+balance, prefix FROM users ORDER BY '
            'deposit+bank+balance DESC LIMIT 200;',
            False,
            True)

    elif 'банк' in arg.lower():
        top_users = sql.execute(
            'SELECT id, first_name, name, username, bank, prefix FROM users ORDER BY bank DESC LIMIT 200;',
            False,
            True)
    elif 'депозит' in arg.lower():
        top_users = sql.execute(
            'SELECT id, first_name, name, username, deposit, prefix FROM users ORDER BY deposit DESC LIMIT 200;',
            False,
            True)
    elif 'уровень' in arg.lower():
        top_users = sql.execute(
            'SELECT id, first_name, name, username, level, prefix FROM users ORDER BY level DESC LIMIT 200;',
            False,
            True)
    elif 'реф' in arg.lower():
        top_users = sql.execute(
            'SELECT id, first_name, name, username, refs, prefix FROM users ORDER BY refs DESC LIMIT 200;',
            False,
            True)
    elif 'баланс' in arg.lower() or 'б' in arg.lower():
        top_users = sql.execute(
            'SELECT id, first_name, name, username, balance, prefix FROM users ORDER BY balance DESC LIMIT 200;',
            False,
            True)
    elif 'клан' in arg.lower():
        top_clan = sql.execute('SELECT id, name, win,prefix FROM clans ORDER BY win DESC LIMIT 200;',
                               False,
                               True)
        text = text.format(
            arg.lower().split()[0] if arg.lower().split()[0] != 'по' else arg.lower().split()[1],
            len(top_clan))
        index = 0
        for clan in top_clan:
            id, name, win, prefix = clan
            if index == 10:
                break
            index += 1
            emoji = ''.join(numbers_emoji[int(i)] for i in str(index))
            text += f'{emoji}. {name + "~[" + prefix + "]" if prefix and name else name} 🆔 <code>{id}</code> — ' \
                    f'🥇 {win}\n'
        text += '➖➖➖➖➖➖➖➖➖➖➖➖\n'
        try:
            clan_user = Clanuser(user_id=message.from_user.id)
        except Exception:
            clan_user = None
            text += 'Вы не состоите в клане!'
        if clan_user:
            for index, clan in enumerate(top_clan, start=1):
                if clan[0] == clan_user.id_clan:
                    id, name, win, prefix = clan
                    emoji = ''.join(numbers_emoji[int(i)] for i in str(index))
                    text += f'{emoji}. {name + "~[" + prefix + "]" if prefix and name else name} 🆔 <code>{id}</code> — ' \
                            f'🥇 {win}\n'
                    break
                if index == 200:
                    text += 'Ваш клан не входит в топ 200!\n'
                    break
        return await message.reply(text=text, disable_web_page_preview=True,
                                   reply_markup=top_kb_func(message.from_user.id).as_markup())
    else:
        return await message.reply(text="❌ Ошибка , Такого топа не существует!", disable_web_page_preview=True,
                                   reply_markup=top_kb_func(message.from_user.id).as_markup())

    try:
        text = text.format(
            arg.lower().split()[0] if arg.lower().split()[0] != 'по' else arg.lower().split()[1],
            len(top_users))
    except IndexError:
        text = text.format('общий', len(top_users))

    index = 0
    for user in top_users:
        user_id, first_name, name, username, balance, prefix = user
        user2 = User(id=user_id)
        donate_source = user2.donate_source
        try:
            donate_source = int(donate_source.split(',')[0])
        except AttributeError:
            donate_source = None
        if donate_source == None or donate_source != 5 and donate_source != 6:
            if index == 10:
                break

            index += 1
            emoji = ''.join(numbers_emoji[int(i)] for i in str(index))
            link = user2.link if user2.notifies else f'<a href="https://t.me/{bot_name}">{name if name else first_name}</a>'
            text += f'{emoji}. {prefix + " " if prefix and name else ""}{link} - (<code>{user_id}</code>) - ' \
                    f'{to_str2(transform(balance)) if not (True in [i in arg.lower() for i in ["уровень", "реф", "лвл"]]) else balance}\n'

    text += '➖➖➖➖➖➖➖➖➖➖➖➖\n'
    for index, user_s in enumerate(top_users, start=1):
        if user_s[0] == message.from_user.id:
            index = index
            user2 = User(id=message.from_user.id)
            emoji = ''.join(numbers_emoji[int(i)] for i in str(index))
            user_id, first_name, name, username, balance, prefix = user_s
            link = user2.link if user2.notifies else f'<a href="https://t.me/{bot_name}">{name if name else first_name}</a>'
            text += f'{emoji}. {prefix + " " if prefix and name else ""}{link} - (<code>{user_id}</code>) - ' \
                    f'{to_str2(transform(balance)) if not (True in [i in arg.lower() for i in ["уровень", "реф", "лвл"]]) else balance}\n'
            break
        if index == 200:
            text += 'Вы не входите в топ 200!\n'
            break
    return await message.reply(text=text, disable_web_page_preview=True,
                               reply_markup=top_kb_func(message.from_user.id).as_markup())


@flags.throttling_key('default')
async def top_handler_call(callback: CallbackQuery):
    text = '🔝 10 Пользователей по ({}):\n<i>📢 Всего пользователей: {}</i>\n\n'
    arg = callback.data.split('_')[1]
    id = int(callback.data.split('_')[2])
    if id != callback.from_user.id:
        return await callback.answer("❌ Не трожь не твое")
    if arg == 'общ':

        top_users = sql.execute(
            'SELECT id, first_name, name, username, deposit+bank+balance, prefix FROM users ORDER BY '
            'deposit+bank+balance DESC LIMIT 200;',
            False,
            True)

    elif arg == 'банк':
        top_users = sql.execute(
            'SELECT id, first_name, name, username, bank, prefix FROM users ORDER BY bank DESC LIMIT 200;',
            False,
            True)
    elif arg == 'депозит':
        top_users = sql.execute(
            'SELECT id, first_name, name, username, deposit, prefix FROM users ORDER BY deposit DESC LIMIT 200;',
            False,
            True)
    elif arg == 'лвл':
        top_users = sql.execute(
            'SELECT id, first_name, name, username, level, prefix FROM users ORDER BY level DESC LIMIT 200;',
            False,
            True)
    elif arg == 'реф':
        top_users = sql.execute(
            'SELECT id, first_name, name, username, refs, prefix FROM users ORDER BY refs DESC LIMIT 200;',
            False,
            True)
    elif arg == 'балансу':
        top_users = sql.execute(
            'SELECT id, first_name, name, username, balance, prefix FROM users ORDER BY balance DESC LIMIT 200;',
            False,
            True)
    elif 'клан' in arg.lower():
        top_clan = sql.execute('SELECT id, name, win,prefix FROM clans ORDER BY '
                               'win DESC LIMIT 200;',
                               False,
                               True)

        text = text.format(
            arg.lower().split()[0] if arg.lower().split()[0] != 'по' else arg.lower().split()[1],
            len(top_clan))

        index = 0
        for clan in top_clan:
            id, name, win, prefix = clan
            if index == 10:
                break
            index += 1
            emoji = ''.join(numbers_emoji[int(i)] for i in str(index))
            text += f'{emoji}. {name + "~[" + prefix + "]" if prefix and name else name} 🆔 <code>{id}</code> — ' \
                    f'🥇 {win}\n'
        text += '➖➖➖➖➖➖➖➖➖➖➖➖\n'
        try:
            clan_user = Clanuser(user_id=callback.from_user.id)
        except Exception:
            clan_user = None
            text += 'Вы не состоите в клане!'
        if clan_user:
            for index, clan in enumerate(top_clan, start=1):
                if clan[0] == clan_user.id_clan:
                    id, name, win, prefix = clan
                    emoji = ''.join(numbers_emoji[int(i)] for i in str(index))
                    text += f'{emoji}. {name + "~[" + prefix + "]" if prefix and name else name} 🆔 <code>{id}</code> — ' \
                            f'🥇 {win}\n'
                    break
                if index == 200:
                    text += 'Ваш клан не входит в топ 200!\n'
                    break

        return await callback.message.edit_text(text=text, disable_web_page_preview=True,
                                                reply_markup=top_back_func(callback.from_user.id).as_markup())
    else:
        return await callback.message.edit_text(text="❌ Ошибка , Такого топа не существует!",
                                                disable_web_page_preview=True,
                                                reply_markup=top_kb_func(callback.from_user.id).as_markup())
    try:
        text = text.format(
            arg.lower().split()[0] if arg.lower().split()[0] != 'по' else arg.lower().split()[1],
            len(top_users))
    except IndexError:
        text = text.format('общий', len(top_users))

    index = 0
    for user in top_users:
        user_id, first_name, name, username, balance, prefix = user
        user2 = User(id=user_id)
        donate_source = user2.donate_source
        try:
            donate_source = int(donate_source.split(',')[0])
        except AttributeError:
            donate_source = None
        if donate_source == None or donate_source != 5 and donate_source != 6:
            if index == 10:
                break
            index += 1
            emoji = ''.join(numbers_emoji[int(i)] for i in str(index))

            link = user2.link if user2.notifies else f'<a href="https://t.me/{bot_name}">{name if name else first_name}</a>'
            text += f'{emoji}. {prefix + " " if prefix and name else ""}{link} - (<code>{user_id}</code>) - ' \
                    f'{to_str2(transform(balance)) if not (True in [i in arg.lower() for i in ["уровень", "реф", "лвл"]]) else balance}\n'
    text += '➖➖➖➖➖➖➖➖➖➖➖➖\n'
    for index, user_s in enumerate(top_users, start=1):
        if user_s[0] == callback.from_user.id:
            index = index
            user2 = User(id=callback.from_user.id)
            emoji = ''.join(numbers_emoji[int(i)] for i in str(index))
            user_id, first_name, name, username, balance, prefix = user_s
            link = user2.link if user2.notifies else f'<a href="https://t.me/{bot_name}">{name if name else first_name}</a>'
            text += f'{emoji}. {prefix + " " if prefix and name else ""}{link} - (<code>{user_id}</code>) - ' \
                    f'{to_str2(transform(balance)) if not (True in [i in arg.lower() for i in ["уровень", "реф", "лвл"]]) else balance}\n'
            break
        if index == 200:
            text += 'Вы не входите в топ 200!\n'
            break
    return await callback.message.edit_text(text=text, disable_web_page_preview=True,
                                            reply_markup=top_back_func(id).as_markup())
    # 2.16850209236145


@flags.throttling_key('default')
async def topback_handler_call(callback: CallbackQuery):
    id = int(callback.data.split('_')[1])
    if id != callback.from_user.id:
        return await callback.answer("❌ Не трожь не твое")
    text = '🔝 10 Пользователей по ({}):\n<i>📢 Всего пользователей: {}</i>\n\n'

    top_users = sql.execute('SELECT id, first_name, name, username, deposit+bank+balance, prefix FROM users ORDER BY '
                            'deposit+bank+balance DESC LIMIT 200;',
                            False,
                            True)

    text = text.format('общий', len(top_users))
    index = 0
    for user in top_users:
        user_id, first_name, name, username, balance, prefix = user
        user2 = User(id=user_id)
        donate_source = user2.donate_source
        try:
            donate_source = int(donate_source.split(',')[0])
        except AttributeError:
            donate_source = None
        if donate_source == None or donate_source != 5 and donate_source != 6:
            if index == 10:
                break
            index += 1
            emoji = ''.join(numbers_emoji[int(i)] for i in str(index))
            link = user2.link if user2.notifies else f'<a href="https://t.me/{bot_name}">{name if name else first_name}</a>'
            text += f'{emoji}. {prefix + " " if prefix and name else ""}{link} - (<code>{user_id}</code>) - ' \
                    f'{to_str2(transform(balance))}\n'
    text += '➖➖➖➖➖➖➖➖➖➖➖➖\n'
    for index, user_s in enumerate(top_users, start=1):
        if user_s[0] == callback.from_user.id:
            index = index
            user2 = User(id=callback.from_user.id)
            emoji = ''.join(numbers_emoji[int(i)] for i in str(index))
            user_id, first_name, name, username, balance, prefix = user_s
            link = user2.link if user2.notifies else f'<a href="https://t.me/{bot_name}">{name if name else first_name}</a>'
            text += f'{emoji}. {prefix + " " if prefix and name else ""}{link} - (<code>{user_id}</code>) - ' \
                    f'{to_str2(transform(balance))}\n'
            break
        if index == 200:
            text += 'Вы не входите в топ 200!\n'
            break
    return await callback.message.edit_text(text=text, disable_web_page_preview=True,
                                            reply_markup=top_kb_func(id).as_markup())
