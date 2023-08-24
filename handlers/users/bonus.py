from datetime import datetime, timedelta

from aiogram import flags
from aiogram.types import Message

from loader import bot
from utils.main.cash import to_str
from utils.main.donates import to_str as to_strs
from utils.main.users import User
from utils.quests.main import QuestUser

day = 60 * 60 * 24


@flags.throttling_key('default')
async def bonus_handler(message: Message):
    user = User(user=message.from_user)
    dop = '\n\nДобавь к своему телеграм описанию или фамилии "@pegasusgame_bot" и <b>получай +50% к бонусу</b>'
    if (datetime.now() - user.bonus).total_seconds() < day and datetime.now().day <= user.bonus.day:
        return await message.reply('❌ Вы уже забирали ежедневный бонус\n'
                                   f'⏳ Следующий через: <code>'
                                   f'{to_strs((user.bonus + timedelta(days=1)) - datetime.now())}</code>' + dop)
    else:
        name = message.from_user.full_name
        if message.chat.id == message.from_user.id and message.chat.description:
            name += f' {message.chat.description}'
        else:
            user_info = await bot.get_chat(message.from_user.id)  # тут информация о профиле
            name = user_info.bio
        bonus = user.get_bonus(name)
        dop_bonus = user.refs * 5_000

    await message.reply(f'✅ Вы активировали ежедневный бонус,'
                        f' на ваш баланс зачислено +{to_str(bonus - dop_bonus)}\n🎁 дополнительный бонус за реф. {to_str(dop_bonus)}')
    result = QuestUser(user_id=user.id).update_progres(quest_ids=[8, 9], add_to_progresses=[bonus + dop_bonus, 1])
    if result != '':
        await message.answer(text=result.format(user=user.link), disable_web_page_preview=True)
    return
