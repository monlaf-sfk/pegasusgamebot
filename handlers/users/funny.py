import random

from aiogram import flags
from aiogram.types import Message

from utils.main.users import User


@flags.throttling_key('default')
async def globus_handler(message: Message):
    if len(message.text.split()) == 1:
        emoji = ['▶️', '❔', '💡', '❓', '✅', '➡️']
        g2 = random.choice(emoji)
        return await message.reply(f"{g2} Используйте «Шар [вопрос]»")

    h = ["Мой ответ - нет", "Мне кажется - да", "Сейчас нельзя предсказать",
         "хорошие перспективы", "весьма сомнительно", "предрешено", "сконцентрируйся и спроси опять",
         "Мне кажется - нет", "Знаки говорят - нет", " знаки говорят - «Да»",
         "бесспорно", "можешь быть уверен в этом", "лучше не рассказывать", "спроси позже",
         "Да", "Нет", "никаких сомнений", "перспективы не очень хорошие"]
    g = random.choice(h)
    user = User(id=message.from_user.id)
    await message.reply(f"""🔮 {user.link}, {g} """, disable_web_page_preview=True)


@flags.throttling_key('default')
async def chance_handler(message: Message):
    if len(message.text.split()) == 1:
        emoji = ['▶️', '❔', '💡', '❓', '✅', '➡️']
        g2 = random.choice(emoji)
        return await message.reply(f"{g2} Используйте «Шанс [предложение]»")

    h = ["мне кажется около", "шанс этого", "вероятность этого",
         "шанс этого не меньше", "я думаю где-то", "вероятность"]
    g = random.choice(h)
    procent = random.randint(0, 100)
    user = User(id=message.from_user.id)
    await message.reply(f"""📊 {user.link}, {g} {procent}%""", disable_web_page_preview=True)


@flags.throttling_key('default')
async def choice_handler(message: Message):
    arg = message.text.lower().replace('выбери', '')
    if 'или' not in arg:
        emoji = ['▶️', '❔', '💡', '❓', '✅', '➡️']
        g2 = random.choice(emoji)
        return await message.reply(f"{g2} Используйте «Выбери [текст] или [текст]»")
    arg = arg.split('или')

    if len(arg) < 2:
        emoji = ['▶️', '❔', '💡', '❓', '✅', '➡️']
        g2 = random.choice(emoji)
        return await message.reply(f"{g2} Используйте «Выбери [текст] или [текст]»")

    h = [f"я не уверен, но выберу «{arg[0]}»",
         f"я не уверен, но выберу «{arg[1]}»",
         f"как по мне, «{arg[0]}» лучше, но «{arg[1]}» тоже неплохо",
         f"как по мне, «{arg[1]}» лучше, но «{arg[1]}» тоже неплохо",
         f"нет ничего лучше «{arg[0]}»",
         f"нет ничего лучше «{arg[1]}»",
         f"конечно «{arg[0]}»",
         f"конечно «{arg[1]}»",
         f"очевидно, что «{arg[0]}» лучше!",
         f"очевидно, что «{arg[1]}» лучше!",
         f"очевидно, что «{arg[0]}» гораздо лучше!",
         f"очевидно, что «{arg[1]}» гораздо лучше!",
         f"нет ничего лучше «{arg[0]}»",
         f"нет ничего лучше «{arg[1]}»",
         f"мне кажется, лучше «{arg[0]}», чем «{arg[1]}»",
         f"мне кажется, лучше «{arg[1]}», чем «{arg[0]}»",
         f"100% «{arg[1]}» намного лучше",
         f"100% «{arg[0]}» намного лучше",
         f"конечно «{arg[0]}» лучше!",
         f"конечно «{arg[1]}» лучше!"]
    g = random.choice(h)
    user = User(id=message.from_user.id)
    await message.reply(f"""⚖️ {user.link}, {g}  """, disable_web_page_preview=True)
