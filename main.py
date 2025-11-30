import asyncio
import logging
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

# Try to import RedisStorage (optional)
try:
    from aiogram.fsm.storage.redis import RedisStorage
except Exception:
    RedisStorage = None

from handlers import form_router, vacancies_router, admin_router
from utils import init_excel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
REDIS_URL = os.getenv("REDIS_URL")
if not TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN not set in environment")

async def main() -> None:
    init_excel()

    bot = Bot(token=TOKEN, parse_mode="HTML")

    # Choose storage: Redis if REDIS_URL provided and RedisStorage available, else Memory
    if REDIS_URL and RedisStorage is not None:
        try:
            storage = RedisStorage.from_url(REDIS_URL)
            logger.info("Using RedisStorage for FSM")
        except Exception as e:
            logger.warning("Failed to initialize RedisStorage (%s), falling back to MemoryStorage", e)
            storage = MemoryStorage()
    else:
        storage = MemoryStorage()
        if REDIS_URL and RedisStorage is None:
            logger.warning("REDIS_URL is set but aiogram RedisStorage is not available (missing dependency). Using MemoryStorage.")

    dp = Dispatcher(storage=storage)

    # include routers
    dp.include_router(form_router)
    dp.include_router(vacancies_router)
    dp.include_router(admin_router)

    try:
        logger.info("Starting aiogram bot (aiogram 3.22)...")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())