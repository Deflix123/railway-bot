import aiohttp
import asyncio
import os
from io import BytesIO
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# Берём токен из переменных окружения (безопасно)
TOKEN = os.getenv('BOT_TOKEN')

# Проверяем, есть ли токен
if not TOKEN:
    print("ОШИБКА: Не найден токен! Добавьте переменную BOT_TOKEN в настройках Render")
    exit(1)

# Бесплатный API Pollinations
POLLINATIONS_URL = "https://image.pollinations.ai/prompt/"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

def build_prompt(greeting_type: str, user_text: str) -> str:
    base_style = "beautiful natural landscape, soft colors, high resolution, background for text, empty space for text"

    if greeting_type == "morning":
        return f"Morning sunrise, golden hour, dew on grass, sunny meadow, {base_style}. Text: {user_text}"
    elif greeting_type == "day":
        return f"Bright sunny day, blue sky with clouds, green forest, river, summer vibe, {base_style}. Text: {user_text}"
    elif greeting_type == "night":
        return f"Night sky, bright moon, stars, calm lake reflection, deep blue colors, cozy atmosphere, {base_style}. Text: {user_text}"
    else:
        return f"{base_style}. Text: {user_text}"

async def generate_image(prompt: str) -> BytesIO:
    encoded_prompt = aiohttp.helpers.quote(prompt)
    request_url = f"{POLLINATIONS_URL}{encoded_prompt}?nologo=true&width=1024&height=1024"

    async with aiohttp.ClientSession() as session:
        async with session.get(request_url) as response:
            if response.status == 200:
                img_data = await response.read()
                return BytesIO(img_data)
            else:
                raise Exception(f"Ошибка: {response.status}")

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(
        "🌄 Привет! Я использую **нейросеть Flux**, чтобы рисовать красивые пейзажи.\n\n"
        "Просто напиши:\n"
        "• *доброе утро*\n"
        "• *хорошего дня*\n"
        "• *спокойной ночи*\n\n"
        "Или добавь свой текст, например: *спокойной ночи, любимая*"
    )

@dp.message_handler()
async def handle_message(message: types.Message):
    text_lower = message.text.lower()
    greeting_type = None
    final_text = message.text

    if "доброе утро" in text_lower or "morning" in text_lower:
        greeting_type = "morning"
    elif "хорошего дня" in text_lower or "добрый день" in text_lower:
        greeting_type = "day"
    elif "спокойной ночи" in text_lower or "night" in text_lower:
        greeting_type = "night"
    else:
        await message.answer("😊 Напиши: *доброе утро*, *хорошего дня* или *спокойной ночи*")
        return

    await bot.send_chat_action(message.chat.id, "upload_photo")

    try:
        prompt = build_prompt(greeting_type, final_text)
        image_bytes = await generate_image(prompt)
        
        await message.answer_photo(
            photo=types.InputFile(image_bytes, filename="wish.png"),
            caption=f"✨ *{final_text}* ✨\n\n🎨 *Сгенерировано нейросетью*"
        )
    except Exception as e:
        await message.answer("😔 Ошибка! Попробуйте ещё раз через минуту.")
        print(f"Ошибка: {e}")

if __name__ == '__main__':
    print("🚀 Бот запущен!")
    executor.start_polling(dp, skip_updates=True)