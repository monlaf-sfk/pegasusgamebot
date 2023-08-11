import random
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode
from PIL import Image, ImageDraw

API_TOKEN = 'YOUR_API_TOKEN'  # Замените на ваш API токен

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

correct_cup = random.randint(1, 3)


def generate_cup_game_image(correct_cup):
    image = Image.new("RGB", (600, 400), "white")
    draw = ImageDraw.Draw(image)

    cup_width = 150
    cup_height = 200
    cup_spacing = 160
    cup_top = 100
    cup_colors = ["#ffd700", "#32cd32", "#4169e1"]

    for i in range(3):
        cup_left = (image.width - (cup_width * 3 + cup_spacing * 2)) / 2 + i * (cup_width + cup_spacing)
        cup_right = cup_left + cup_width

        draw.polygon([(cup_left, cup_top + cup_height), (cup_right, cup_top + cup_height),
                      ((cup_left + cup_right) / 2, cup_top + cup_height + 30)], fill=cup_colors[i])
        draw.rectangle([cup_left + 25, cup_top, cup_right - 25, cup_top + cup_height], outline="black", width=3)

        if i + 1 == correct_cup:
            ball_x = (cup_left + cup_right) / 2
            ball_y = cup_top + cup_height - 60
            ball_radius = 30
            draw.ellipse((ball_x - ball_radius, ball_y - ball_radius, ball_x + ball_radius, ball_y + ball_radius),
                         fill="white")

    return image


@dp.message_handler(commands=['start'])
async def start_game(message: types.Message):
    global correct_cup
    correct_cup = random.randint(1, 3)

    image = generate_cup_game_image(correct_cup)
    with open("cup_game_image.png", "wb") as image_file:
        image.save(image_file, format="PNG")

    await bot.send_photo(message.chat.id, photo=open("cup_game_image.png", "rb"))
    await message.reply("Привет! Давай сыграем в игру со стаканчиками. В каком стакане шарик? (1, 2 или 3)")


@dp.message_handler(lambda message: message.text in ['1', '2', '3'])
async def check_answer(message: types.Message):
    user_answer = int(message.text)
    if user_answer == correct_cup:
        response_text = "Верно! Шарик действительно был в стакане {}.".format(correct_cup)
    else:
        response_text = "Неверно! Шарик был в стакане {}.".format(correct_cup)

    await message.reply(response_text)

    correct_cup = random.randint(1, 3)
    image = generate_cup_game_image(correct_cup)
    with open("cup_game_image.png", "wb") as image_file:
        image.save(image_file, format="PNG")

    await bot.send_photo(message.chat.id, photo=open("cup_game_image.png", "rb"))
    await message.reply("Сыграем еще раз? В каком стакане будет шарик? (1, 2 или 3)")


if __name__ == '__main__':
    from aiogram import executor

    executor.start_polling(dp, skip_updates=True)
