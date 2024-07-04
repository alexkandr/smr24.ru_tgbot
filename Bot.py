from os import getenv
import asyncio
import logging
import pathlib

load_dotenv()
TOKEN =  getenv('BOT_TOKEN')
IS_DEBUG = getenv('IS_DEBUG')

rel_path = pathlib.Path(__file__).parent.resolve()
with open(rel_path.joinpath('./logs/number.log'), 'r+') as n:
    curr = int(n.read())
    n.seek(0, 0)
    n.write(str(curr+1))
logging.basicConfig(level=logging.INFO if IS_DEBUG else logging.DEBUG, 
                    filename=str(rel_path.joinpath(f"./logs/logs{curr}.log")),
                    filemode="w",
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s", force=True)

from dotenv import load_dotenv
from aiogram import Dispatcher, Bot
from aiogram.fsm.strategy import FSMStrategy
from aiogram.fsm.storage.memory import MemoryStorage

from routers import menu, catalog, cart, address, purchase, search, order




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
    dp.include_router(order.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main(), debug=True)

