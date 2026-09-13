import os
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ContentType
import asyncio

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
API_URL = "http://localhost:8000/distribute"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer("Send a video + caption. I will distribute to all platforms.")

@dp.message(lambda m: m.content_type == ContentType.VIDEO)
async def handle_video(msg: types.Message):
    video = msg.video
    file = await bot.get_file(video.file_id)
    dest = f"/tmp/{video.file_id}.mp4"
    await bot.download_file(file.file_path, dest)
    caption = msg.caption or ""
    async with aiohttp.ClientSession() as session:
        payload = {"video_path": dest, "caption": caption, "hashtags": ""}
        async with session.post(API_URL, json=payload) as resp:
            data = await resp.json()
            await msg.answer(f"Queued: {data}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
