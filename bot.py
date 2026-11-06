import os
import re
import urllib.parse
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

MINI_APP_URL = "https://test-stream-player.supershort80.workers.dev"
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN missing!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

URL_REGEX = r"https?:\/\/[^\s]+"

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("👋 Bot online hai! Koi bhi TeraBox link bhejo.")

@dp.message(F.text)
async def handle_link(message: types.Message):
    match = re.search(URL_REGEX, message.text.strip())
    if not match:
        await message.reply("⚠️ Kripya valid link bhejein.")
        return

    terabox_url = match.group(0)

    # Clean encoded URL parameter
    safe_param = urllib.parse.quote(terabox_url, safe='')
    final_url = f"{MINI_APP_URL}/?tera_url={safe_param}"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="▶ Watch in Telegram (Mini App)", 
                    web_app=WebAppInfo(url=final_url)
                )
            ],
            [
                InlineKeyboardButton(
                    text="🌐 Watch in Browser (Fallback)", 
                    url=final_url
                )
            ]
        ]
    )

    await message.reply(
        "🎬 **Stream Ready!**\n\nNeeche diye gaye button par tap karein:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

# Render dummy port
async def handle_health(request):
    return web.Response(text="Bot OK")

async def start_dummy():
    app = web.Application()
    app.router.add_get("/", handle_health)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await asyncio.gather(start_dummy(), dp.start_polling(bot, drop_pending_updates=True))

if __name__ == "__main__":
    asyncio.run(main())
    
