import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers.common import common_router
from handlers.main_menu_handlers import main_menu_router
from handlers.request_handlers import request_router
from handlers.admin_handlers import admin_router


logging.basicConfig(level=logging.INFO)


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Регистрация роутеров
    dp.include_router(admin_router)
    dp.include_router(request_router)
    dp.include_router(common_router)
    dp.include_router(main_menu_router)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
