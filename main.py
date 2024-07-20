from aiogram import Bot, Dispatcher
from app.handlers import router
import asyncio
import logging


TOKEN_API = '7399665611:AAGtybvKJU8Ey0YyOQE5W3-H0q1ETytWxVE'
bot = Bot(token=TOKEN_API)
dp = Dispatcher(bot=bot)


async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
