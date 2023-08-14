import random
import re

from aiogram import flags
from aiogram.types import Message

from utils.main.users import User
from utils.quests.main import QuestUser


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
    result = QuestUser(user_id=user.id).update_progres(quest_ids=18, add_to_progresses=1)
    if result != '':
        await message.answer(text=result.format(user=user.link), disable_web_page_preview=True)


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
    result = QuestUser(user_id=user.id).update_progres(quest_ids=22, add_to_progresses=1)
    if result != '':
        await message.answer(text=result.format(user=user.link), disable_web_page_preview=True)


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
    result = QuestUser(user_id=user.id).update_progres(quest_ids=21, add_to_progresses=1)
    if result != '':
        await message.answer(text=result.format(user=user.link), disable_web_page_preview=True)


rotateText = {
    'q': 'q',
    'w': 'ʍ',
    'e': 'ǝ',
    'r': 'ɹ',
    't': 'ʇ',
    'y': 'ʎ',
    'u': 'u',
    'i': 'ᴉ',
    'o': 'o',
    'p': 'p',
    'a': 'ɐ',
    's': 's',
    'd': 'd',
    'f': 'ɟ',
    'g': 'ƃ',
    'h': 'ɥ',
    'j': 'ɾ',
    'k': 'ʞ',
    'l': 'l',
    'z': 'z',
    'x': 'x',
    'c': 'ɔ',
    'v': 'ʌ',
    'b': 'b',
    'n': 'n',
    'm': 'ɯ',
    'й': 'ņ',
    'ц': 'ǹ',
    'у': 'ʎ',
    'к': 'ʞ',
    'е': 'ǝ',
    'н': 'н',
    'г': 'ɹ',
    'ш': 'm',
    'щ': 'm',
    'з': 'ε',
    'х': 'х',
    'ъ': 'q',
    'ф': 'ф',
    'ы': 'ıq',
    'в': 'ʚ',
    'а': 'ɐ',
    'п': 'u',
    'р': 'd',
    'о': 'о',
    'л': 'v',
    'д': 'ɓ',
    'ж': 'ж',
    'э': 'є',
    'я': 'ʁ',
    'ч': 'һ',
    'с': 'ɔ',
    'м': 'w',
    'и': 'и',
    'т': 'ɯ',
    'ь': 'q',
    'б': 'ƍ',
    'ю': 'oı',
    '!': '¡',
    '?': '¿',
    '.': '˙',
    ',': '\'',
    '\'': ',',
    '\"': '„',
    '`': ',',
    '(': ')',
    ')': '(',
    '<': '>',
    '>': '<',
    '{': '}',
    '}': '{',
    '[': ']',
    ']': '[',
    '&': '⅋',
    '@': '@',
    '#': '#',
    '$': '$',
    '%': '%',
    '^': '^',
    '*': '*',
    '+': '⁺',
    '-': '-',
    '=': '=',
    '/': '/',
    '\\': '\\',
    '|': '|',
    '_': '_',
    '~': '⁓',
}


async def process_rotate_command(text):
    reversed_text = ''
    for char in text:
        if char in rotateText:
            reversed_text += rotateText[char]
        else:
            reversed_text += char
    reversed_text = reversed_text[::-1]  # Reverse the text
    return f'держи: "{reversed_text}"'


async def reverse_handler(message: Message):
    match = re.match(r'^переверни\s(.*)$', message.text, re.IGNORECASE)
    if match:
        text_to_rotate = match.group(1)[:350]
        result = await process_rotate_command(text_to_rotate)
        await message.reply(result)
    else:
        await message.reply("❔ Используйте «Переверни [текст до 350 символов]»")
