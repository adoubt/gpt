import asyncio
from loguru import logger
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from src.handlers import user_handler
from src.misc import bot, dp

def register_handlers():
    dp.include_routers(user_handler.router)


async def main():
    register_handlers()
    
    await dp.start_polling(bot)
if __name__ == "__main__":
    logger.add('src/logs/logs.log', format="{time} {level} {message}", level='DEBUG')  # Объект бота 
    
    asyncio.run(main())
