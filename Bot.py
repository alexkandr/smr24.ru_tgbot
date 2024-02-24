from os import getenv
import asyncio
import logging

from dotenv import load_dotenv
from aiogram import Dispatcher, Bot
from aiogram.fsm.strategy import FSMStrategy
from aiogram.fsm.storage.memory import MemoryStorage

from routers import menu, catalog, cart, address, purchase, search
from models.db import images_tab

load_dotenv()
TOKEN =  getenv('BOT_TOKEN')
logging.basicConfig(level=logging.INFO, filename="./logs/py_log.log",filemode="w")


async def main():
    logging.info('Starting Bot')
    try:
        bot = Bot(token=TOKEN, parse_mode='HTML')
        dp = Dispatcher(fsm_strategy=FSMStrategy.USER_IN_CHAT, storage=MemoryStorage()) 
    except:
        logging.error('couldnt connect to telegram api')
    logging.info('Bot started')
    #await images_tab.upload_(bot)
    dp.include_router(menu.router)
    dp.include_router(catalog.router)
    dp.include_router(cart.router)
    dp.include_router(address.router)
    dp.include_router(purchase.router)
    dp.include_router(search.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main(), debug=True)

