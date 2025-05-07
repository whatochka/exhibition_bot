from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
import asyncio
import logging
import os

from app.handlers import register_all_handlers
from app.utils.db import create_db_pool

from dotenv import load_dotenv

load_dotenv()


async def main():
    logging.basicConfig(level=logging.INFO)

    bot = Bot(
        token=os.getenv("BOT_TOKEN"),
        parse_mode=ParseMode.HTML
    )

    dp = Dispatcher(storage=RedisStorage.from_url(os.getenv("REDIS_URL")))

    await create_db_pool()

    register_all_handlers(dp)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
