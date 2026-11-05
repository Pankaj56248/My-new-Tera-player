import os
import re
import urllib.parse
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# Aapka Cloudflare Worker URL
MINI_APP_URL = "https://test-stream-player.supershort80.workers.dev/"
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable set nahi hai!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

TERA_REGEX = r"https?:\/\/[^\s]+"

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("👋 Testing Bot Active hai!\n\nKoi bhi TeraBox link bhejo, seedha Mini App me chalega.")

@dp.message(F.text)
async def handle_link(message: types.Message):
    user_text = message.text.strip()
    match = re.search(TERA_REGEX, user_text)
    if not match:
        return

    terabox_url = match.group(0)

    # TeraBox link ko seedha Mini App me bhej do (Resolution Mini App khud karega)
    encoded_url = urllib.parse.quote(terabox_url, safe='')
    final_url = f"{MINI_APP_URL}?tera_url={encoded_url}"

    btn = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="▶ Play Video (Instant)", web_app=WebAppInfo(url=final_url))]
        ]
    )

    await message.reply(
        "🎬 **Video Link Ready!**\n\nNeeche button par tap karein, Mini App bina kisi server error ke link resolve karke video chala dega:",
        reply_markup=btn,
        parse_mode="Markdown"
    )

# Render dummy port taaki service 24/7 live rahe
async def handle_health_check(request):
    return web.Response(text="Bot is running!")

async def start_dummy_server():
    app = web.Application()
    app.router.add_get("/", handle_health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await asyncio.gather(
        start_dummy_server(),
        dp.start_polling(bot, drop_pending_updates=True)
    )

if __name__ == "__main__":
    asyncio.run(main())
    
