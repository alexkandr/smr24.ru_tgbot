from os import getenv
import asyncio
import logging
import pathlib

rel_path = pathlib.Path(__file__).parent.resolve()
logging.basicConfig(level=logging.INFO, 
                    filename=str(rel_path.joinpath("./logs/logs.log")),
                    filemode="w",
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s", force=True)

from dotenv import load_dotenv
from aiogram import Dispatcher, Bot
from aiogram.fsm.strategy import FSMStrategy
from aiogram.fsm.storage.memory import MemoryStorage

from routers import menu, catalog, cart, address, purchase, search

load_dotenv()
TOKEN =  getenv('BOT_TOKEN')



logger = logging.getLogger(__name__)

async def main():
    logger.info('Starting Bot')
    try:
        bot = Bot(token=TOKEN, parse_mode='HTML')
        dp = Dispatcher(fsm_strategy=FSMStrategy.USER_IN_CHAT, storage=MemoryStorage()) 
    except:
        logger.error('couldnt connect to telegram api')
    logger.info('Bot started')
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

