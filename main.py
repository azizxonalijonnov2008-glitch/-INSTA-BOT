import asyncio
import logging
import sys

# Windows konsolida UTF-8 va emojilar to'g'ri ishlashi uchun
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from handlers import get_handlers_router


# Logging sozlamalari
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("InstagramBot")

async def main():
    if not BOT_TOKEN or BOT_TOKEN == "SIZNING_BOT_TOKENINGIZ":
        logger.error(
            "\n" + "=" * 60 + "\n"
            "DIQQAT: Bot tokeni topilmadi!\n"
            "Iltimos, .env faylini oching va Telegram @BotFather dan olgan\n"
            "BOT_TOKEN qiymatini kiriting.\n"
            "Misol: BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrs\n"
            + "=" * 60
        )
        return

    logger.info("Bot ishga tushirilmoqda...")

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # Routerlarni ulash
    dp.include_router(get_handlers_router())

    # Eski kutilmagan xabarlarni tozalash (drop pending updates)
    await bot.delete_webhook(drop_pending_updates=True)

    bot_info = await bot.get_me()
    logger.info(f"Bot muvaffaqiyatli ishga tushdi: @{bot_info.username}")
    print("\n" + "=" * 50)
    print(f"🚀 Bot faol: https://t.me/{bot_info.username}")
    print("Instagram havolasini yuborib tekshirib ko'rishingiz mumkin.")
    print("=" * 50 + "\n")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("Bot to'xtatildi.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi!")
