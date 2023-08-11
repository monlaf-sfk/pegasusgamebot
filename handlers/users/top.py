from aiogram import flags
from aiogram.types import Message, CallbackQuery

from config import bot_name
from keyboard.main import top_kb_func, top_back_func
from utils.clan.clan import Clan, Clanuser
from utils.main.cash import transform, to_str2
from utils.main.db import sql

from utils.main.users import all_users

numbers_emoji = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']


async def link_user(username, name, first_name, nick_hyperlink, nick_clanteg, id):
    url = f'https://t.me/{username}' if username else f'tg://user?id={id}'

    if nick_clanteg:
        try:
            clanuser = Clanuser(user_id=id)
            clan = Clan(clan_id=clanuser.clan_id)
        except:
            if nick_hyperlink:
                return f'<a href="{url}">{name if name else first_name}</a>'
            return f'{name if name else first_name}'
        if nick_hyperlink:
            return f'{clan.prefix} <a href="{url}">{name if name else first_name}</a>'
        return f'{clan.prefix} {name if name else first_name}'

    else:
        if nick_hyperlink:
            return f'<a href="{url}">{name if name else first_name}</a>'
        return f'{name if name else first_name}'


@flags.throttling_key('default')
async def top_handler(message: Message):
    text = '🔝 10 Пользователей по ({}):\n<i>📢 Всего пользователей: {}</i>\n\n'
    arg = ' '.join(message.text.split()[1:]) if not bot_name.lower() in message.text.split()[
        0].lower() else message.text.split()[2:]
    arg_lower = arg.lower()
    top_query = """
        SELECT  users.id,  users.first_name,  users.name,  users.username,  
        users.deposit+ users.bank+ users.balance,  users.donate_source, settings.nick_hyperlink, settings.nick_clanteg
        FROM users
        INNER JOIN settings ON users.id = settings.user_id
ORDER BY {} DESC
LIMIT 200;
    """

    if len(arg) == 0 or any(keyword in arg_lower for keyword in ['общ', 'все', 'всё']):
        order_by = 'users.deposit+users.bank+users.balance'
    elif 'банк' in arg_lower:
        order_by = 'users.bank'
    elif 'депозит' in arg_lower:
        order_by = 'users.deposit'
    elif 'уровень' in arg_lower:
        order_by = 'users.level'
    elif 'реф' in arg_lower:
        order_by = 'users.refs'
    elif 'баланс' in arg_lower or 'б' in arg_lower:
        order_by = 'users.balance'
    elif 'клан' in arg_lower:
        top_clan_query = """
            SELECT id, name, win, prefix
            FROM clans
            ORDER BY win DESC
            LIMIT 200;
        """
        top_clan = sql.execute(top_clan_query, False, True)
        text = text.format(
            arg_lower.split()[0] if arg_lower.split()[0] != 'по' else arg_lower.split()[1],
            len(top_clan)
        )
        index = 0
        for clan in top_clan:
            id, name, win, prefix = clan
            if index == 10:
                break
            index += 1
            emoji = ''.join(numbers_emoji[int(i)] for i in str(index))
            text += f'{emoji}. {name + "~" + prefix if prefix and name else name} 🆔 <code>{id}</code> — ' \
                    f'🥇 {win}\n'
        text += '➖➖➖➖➖➖➖➖➖➖➖➖\n'
        try:
            clan_user = Clanuser(user_id=message.from_user.id)
        except Exception:
            clan_user = None
            text += 'Вы не состоите в клане!'
        if clan_user:
            for index, clan in enumerate(top_clan, start=1):
                if clan[0] == clan_user.clan_id:
                    id, name, win, prefix = clan
                    emoji = ''.join(numbers_emoji[int(i)] for i in str(index))
                    text += f'{emoji}. {name + "~" + prefix if prefix and name else name} 🆔 <code>{id}</code> — ' \
                            f'🥇 {win}\n'
                    break
                if index == 200:
                    text += 'Ваш клан не входит в топ 200!\n'
                    break
        return await message.reply(
            text=text,
            disable_web_page_preview=True,
            reply_markup=top_kb_func(message.from_user.id).as_markup()
        )
    else:
        return await message.reply(
            text="❌ Ошибка, Такого топа не существует!",
            disable_web_page_preview=True,
            reply_markup=top_kb_func(message.from_user.id).as_markup()
        )

    top_users_query = top_query.format(order_by)
    top_users = sql.execute(top_users_query, False, True)

    try:
        text = text.format(
            arg_lower.split()[0] if arg_lower.split()[0] != 'по' else arg_lower.split()[1],
            len(all_users())
        )
    except IndexError:
        text = text.format('общий', len(all_users()))

    index = 0
    for user in top_users:
        user_id, first_name, name, username, balance, donate_source, nick_hyperlink, nick_clanteg = user
        try:
            donate_source = int(donate_source.split(',')[0])
        except AttributeError:
            donate_source = None
        if donate_source is None or donate_source != 6:
            if index == 10:
                break
            index += 1
            emoji = ''.join(numbers_emoji[int(i)] for i in str(index))
            link = await link_user(username, name, first_name, nick_hyperlink, nick_clanteg,
                                   user_id) if nick_hyperlink else f'<a href="https://t.me/{bot_name}">{name if name else first_name}</a>'
            text += f'{emoji}. {link} - (<code>{user_id}</code>) - ' \
                    f'{to_str2(transform(balance)) if not (True in [i in arg_lower for i in ["уровень", "реф", "лвл"]]) else balance}\n'

    text += '➖➖➖➖➖➖➖➖➖➖➖➖\n'
    for index, user_s in enumerate(top_users, start=1):
        if user_s['id'] == message.from_user.id:
            emoji = ''.join(numbers_emoji[int(i)] for i in str(index))
            user_id, first_name, name, username, balance, donate_source, nick_hyperlink, nick_clanteg = user_s
            link = await link_user(username, name, first_name, nick_hyperlink, nick_clanteg,
                                   user_id) if nick_hyperlink else f'<a href="https://t.me/{bot_name}">{name if name else first_name}</a>'
            text += f'{emoji}. {link} - (<code>{user_id}</code>) - ' \
                    f'{to_str2(transform(balance)) if not (True in [i in arg_lower for i in ["уровень", "реф", "лвл"]]) else balance}\n'
            break
        if index == 200:
            text += 'Вы не входите в топ 200!\n'
            break

    return await message.reply(
        text=text,
        disable_web_page_preview=True,
        reply_markup=top_kb_func(message.from_user.id).as_markup())


@flags.throttling_key('default')
async def top_handler_call(callback: CallbackQuery):
    text = '🔝 10 Пользователей по ({}):\n<i>📢 Всего пользователей: {}</i>\n\n'
    arg = callback.data.split('_')[1]
    user_id_ = int(callback.data.split('_')[2])

    if user_id_ != callback.from_user.id:
        return await callback.answer("❌ Не трожь не твое")

    arg_lower = arg.lower()
    top_query = """
            SELECT  users.id,  users.first_name,  users.name,  users.username,  
        {},  users.donate_source, settings.nick_hyperlink, settings.nick_clanteg
        FROM users
        INNER JOIN settings ON users.id = settings.user_id
ORDER BY {} DESC
LIMIT 200;

    """

    if arg_lower == 'общ':
        order_by = 'users.deposit+users.bank+users.balance'
    elif arg_lower == 'банк':
        order_by = 'users.bank'
    elif arg_lower == 'депозит':
        order_by = 'users.deposit'
    elif arg_lower == 'лвл':
        order_by = 'users.level'
    elif arg_lower == 'реф':
        order_by = 'users.refs'
    elif arg_lower == 'балансу':
        order_by = 'users.balance'
    elif 'клан' in arg_lower:
        top_clan_query = """
            SELECT id, name, win, prefix
            FROM clans
            ORDER BY win DESC
            LIMIT 200;
        """
        top_clan = sql.execute(top_clan_query, False, True)
        text = text.format(
            arg_lower.split()[0] if arg_lower.split()[0] != 'по' else arg_lower.split()[1],
            len(top_clan)
        )
        index = 0
        for clan in top_clan:
            id, name, win, prefix = clan
            if index == 10:
                break
            index += 1
            emoji = ''.join(numbers_emoji[int(i)] for i in str(index))
            text += f'{emoji}. {name + "~" + prefix if prefix and name else name} 🆔 <code>{id}</code> — ' \
                    f'🥇 {win}\n'
        text += '➖➖➖➖➖➖➖➖➖➖➖➖\n'
        try:
            clan_user = Clanuser(user_id=callback.from_user.id)
        except Exception:
            clan_user = None
        if clan_user:
            for index, clan in enumerate(top_clan, start=1):
                if clan[0] == clan_user.clan_id:
                    id, name, win, prefix = clan
                    emoji = ''.join(numbers_emoji[int(i)] for i in str(index))
                    text += f'{emoji}. {name + "~" + prefix if prefix and name else name} 🆔 <code>{id}</code> — ' \
                            f'🥇 {win}\n'
                    break
                if index == 200:
                    text += 'Ваш клан не входит в топ 200!\n'
                    break
        return await callback.message.edit_text(
            text=text,
            disable_web_page_preview=True,
            reply_markup=top_back_func(callback.from_user.id).as_markup()
        )
    else:
        return await callback.message.edit_text(
            text="❌ Ошибка , Такого топа не существует!",
            disable_web_page_preview=True,
            reply_markup=top_kb_func(callback.from_user.id).as_markup()
        )

    top_users_query = top_query.format(order_by, order_by)
    top_users = sql.execute(top_users_query, False, True)

    try:
        text = text.format(
            arg_lower.split()[0] if arg_lower.split()[0] != 'по' else arg_lower.split()[1],
            len(all_users())
        )
    except IndexError:
        text = text.format('общий', len(all_users()))

    index = 0
    for user in top_users:
        user_id, first_name, name, username, balance, donate_source, nick_hyperlink, clan_teg = user

        try:
            donate_source = int(donate_source.split(',')[0])
        except AttributeError:
            donate_source = None
        if donate_source is None or donate_source != 6:
            if index == 10:
                break
            index += 1
            emoji = ''.join(numbers_emoji[int(i)] for i in str(index))

            link = await link_user(username, name, first_name, nick_hyperlink, clan_teg,
                                   user_id) if nick_hyperlink else f'<a href="https://t.me/{bot_name}">{name if name else first_name}</a>'
            text += f'{emoji}. {link} - (<code>{user_id}</code>) - ' \
                    f'{to_str2(transform(balance)) if not (True in [i in arg_lower for i in ["уровень", "реф", "лвл"]]) else balance}\n'
    text += '➖➖➖➖➖➖➖➖➖➖➖➖\n'
    for index, user_s in enumerate(top_users, start=1):
        if user_s['id'] == callback.from_user.id:
            emoji = ''.join(numbers_emoji[int(i)] for i in str(index))
            user_id, first_name, name, username, balance, donate_source, nick_hyperlink, clan_teg = user_s
            link = await link_user(username, name, first_name, nick_hyperlink, clan_teg,
                                   user_id) if nick_hyperlink else f'<a href="https://t.me/{bot_name}">{name if name else first_name}</a>'

            text += f'{emoji}. {link} - (<code>{user_id}</code>) - ' \
                    f'{to_str2(transform(balance)) if not (True in [i in arg_lower for i in ["уровень", "реф", "лвл"]]) else balance}\n'
            break
        if index == 200:
            text += 'Вы не входите в топ 200!\n'
            break

    return await callback.message.edit_text(
        text=text,
        disable_web_page_preview=True,
        reply_markup=top_back_func(user_id_).as_markup()
    )

    # 2.16850209236145


@flags.throttling_key('default')
async def topback_handler_call(callback: CallbackQuery):
    user_id_ = int(callback.data.split('_')[1])
    if user_id_ != callback.from_user.id:
        return await callback.answer("❌ Не трожь не твое")

    text = '🔝 10 Пользователей по ({}):\n<i>📢 Всего пользователей: {}</i>\n\n'

    top_users_query = """
            SELECT  users.id,  users.first_name,  users.name,  users.username,  
            users.deposit+ users.bank+ users.balance,  users.donate_source, settings.nick_hyperlink, settings.nick_clanteg
            FROM users
            INNER JOIN settings ON users.id = settings.user_id
    ORDER BY deposit+bank+balance DESC
    LIMIT 200;
        """
    top_users = sql.execute(top_users_query, False, True)

    text = text.format('общий', len(all_users()))
    index = 0
    for user in top_users:
        user_id, first_name, name, username, balance, donate_source, nick_hyperlink, clan_teg = user

        try:
            donate_source = int(donate_source.split(',')[0])
        except AttributeError:
            donate_source = None
        if donate_source is None or donate_source != 6:
            if index == 10:
                break
            index += 1
            emoji = ''.join(numbers_emoji[int(i)] for i in str(index))
            link = await link_user(username, name, first_name, nick_hyperlink, clan_teg,
                                   user_id) if nick_hyperlink else f'<a href="https://t.me/{bot_name}">{name if name else first_name}</a>'
            text += f'{emoji}. {link} - (<code>{user_id}</code>) - {to_str2(transform(balance))}\n'

    text += '➖➖➖➖➖➖➖➖➖➖➖➖\n'
    for index, user_s in enumerate(top_users, start=1):
        if user_s['id'] == callback.from_user.id:
            emoji = ''.join(numbers_emoji[int(i)] for i in str(index))
            user_id, first_name, name, username, balance, donate_source, nick_hyperlink, clan_teg = user_s
            link = await link_user(username, name, first_name, nick_hyperlink, clan_teg,
                                   user_id) if nick_hyperlink else f'<a href="https://t.me/{bot_name}">{name if name else first_name}</a>'
            text += f'{emoji}. {link} - (<code>{user_id}</code>) - {to_str2(transform(balance))}\n'
            break
        if index == 200:
            text += 'Вы не входите в топ 200!\n'
            break

    return await callback.message.edit_text(
        text=text,
        disable_web_page_preview=True,
        reply_markup=top_kb_func(user_id_).as_markup()
    )
