from aiogram import Bot, Dispatcher
from app.handlers import router
import asyncio
import logging


TOKEN_API = '7307146668:AAE270HRyagCYhjgUizFPAPygsIPpap37WE'
bot = Bot(token=TOKEN_API)
dp = Dispatcher(bot=bot)


async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
