import os
import re
import urllib.parse
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

from resolver import resolve_terabox_link

# Cloudflare Worker URL
MINI_APP_URL = "https://test-stream-player.supershort80.workers.dev/"
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("CRITICAL: BOT_TOKEN environment variable set nahi hai!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Sabhi possible TeraBox domains
TERA_REGEX = r"https?:\/\/(?:[a-zA-Z0-9\-]+\.)?(?:terabox\.com|1024tera\.com|4funbox\.com|teraboxapp\.com|terasharelink\.com|mirrobox\.com|nephobox\.com|momerybox\.com)\/[^\s]+"

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    print(f"[/start command mila user {message.from_user.id} se]")
    await message.answer("👋 Testing Bot Active hai!\n\nKoi bhi TeraBox video link bhejo, main use stream karne ka button dunga.")

@dp.message(F.text)
async def handle_link(message: types.Message):
    user_text = message.text.strip()
    print(f"[Incoming Message]: {user_text}")

    match = re.search(TERA_REGEX, user_text)
    if not match:
        print("[No TeraBox URL matched in text]")
        await message.reply("⚠️ Yeh valid TeraBox link nahi lag rahi hai. Kripya check karein.")
        return

    terabox_url = match.group(0)
    print(f"[Resolving Link]: {terabox_url}")
    waiting_msg = await message.reply("⏳ Stream link nikaali ja rahi hai, wait karein...")

    try:
        result = await resolve_terabox_link(terabox_url)

        if not result.get("success"):
            err = result.get("error", "Unknown error")
            print(f"[Resolver Failed]: {err}")
            await waiting_msg.edit_text(f"❌ Error: Stream link nahi nikaali ja saki.\nDetails: {err}")
            return

        raw_stream_url = result["stream_url"]
        title = result.get("title", "TeraBox Video")
        source = result.get("resolver_name", "Pool")

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
        print("[Successfully sent Mini App button!]")

    except Exception as e:
        print(f"[Handler Exception]: {e}")
        await waiting_msg.edit_text(f"❌ Script Error: {str(e)}")

# --- Render Web Service ke liye Dummy Port ---
async def handle_health_check(request):
    return web.Response(text="Bot is actively running!")

async def start_dummy_server():
    app = web.Application()
    app.router.add_get("/", handle_health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"Web server port {port} par live hai.")

async def main():
    print("Conflict clear kar rahe hain aur bot start kar rahe hain...")
    
    # CRITICAL: Purane hung conflicts aur pending messages ko flush karna
    await bot.delete_webhook(drop_pending_updates=True)

    # Server aur Polling dono ek sath start honge
    await asyncio.gather(
        start_dummy_server(),
        dp.start_polling(bot, drop_pending_updates=True)
    )

if __name__ == "__main__":
    asyncio.run(main())
        
