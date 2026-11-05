import os
import re
import urllib.parse
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

from resolver import resolve_terabox_link

# Aapka Cloudflare Worker URL
MINI_APP_URL = "https://test-stream-player.supershort80.workers.dev/"
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

TERA_REGEX = r"https?:\/\/(?:www\.)?(?:terabox\.com|1024tera\.com|4funbox\.com|teraboxapp\.com|terasharelink\.com|mirrobox\.com|nephobox\.com)\/[^\s]+"

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("👋 Testing Bot Active hai!\n\nKoi bhi TeraBox link bhejo, check karte hain.")

@dp.message(F.text)
async def handle_link(message: types.Message):
    match = re.search(TERA_REGEX, message.text)
    if not match:
        return

    terabox_url = match.group(0)
    waiting_msg = await message.reply("⏳ Stream link nikaali ja rahi hai...")

    result = await resolve_terabox_link(terabox_url)

    if not result["success"]:
        await waiting_msg.edit_text("❌ Error: Stream link nahi nikaali ja saki.")
        return

    raw_stream_url = result["stream_url"]
    title = result["title"]
    source = result["resolver_name"]

    encoded_url = urllib.parse.quote(raw_stream_url, safe='')
    final_url = f"{MINI_APP_URL}?stream_url={encoded_url}"

    btn = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="▶ Play in Mini App", web_app=WebAppInfo(url=final_url))]
        ]
    )

    await waiting_msg.edit_text(
        f"🎬 **{title}**\n📡 Source: `{source}`\n\nNeeche button par click karke stream karein:",
        reply_markup=btn,
        parse_mode="Markdown"
    )

async def main():
    print("Bot Render par successfully start ho chuka hai...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
  
