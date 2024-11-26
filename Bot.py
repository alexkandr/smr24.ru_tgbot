from os import getenv
import asyncio
import logging
import pathlib

from dotenv import load_dotenv
from aiogram import Dispatcher, Bot
from aiogram.fsm.strategy import FSMStrategy
from aiogram.fsm.storage.memory import MemoryStorage

from models.db import DataBase
from models.middleware import InjectDBContextMiddleware
from routers.address import AddressRouter 
from routers.cart import CartRouter 
from routers.catalog import CatalogRouter 
from routers.menu import MenuRouter 
from routers.order import OrderRouter 
from routers.purchase import PurchaseRouter
from routers.search import SearchRouter


def set_logger(is_debug: bool):
    rel_path = pathlib.Path(__file__).parent.resolve()
    with open(rel_path.joinpath('./logs/number.log'), 'r+') as n:
        curr = int(n.read())
        n.seek(0, 0)
        n.write(str(curr+1))
    
    logging.basicConfig(level=logging.INFO if is_debug else logging.DEBUG, 
                    filename=str(rel_path.joinpath(f"./logs/logs{curr}.log")),
                    filemode="w",
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s", force=True)

async def init_db(conn_info):
    #db = DataBase(logger_name='MainPgDB')
    db = DataBase()
    logging.getLogger("psycopg.pool").setLevel(logging.INFO)
    await db.connect(conn_info)

async def main():
    load_dotenv()
    TOKEN =  getenv('BOT_TOKEN')
    IS_DEBUG = getenv('IS_DEBUG')
    DATABASE_INFO = getenv('DATABASE')
    ADMIN_CHAT_ID = int(getenv('ADMIN_CHAT_ID'))

    set_logger(IS_DEBUG)
    await init_db(DATABASE_INFO)

    logger = logging.getLogger(__name__)
    logger.info('Starting Bot')

    try:
        bot = Bot(token=TOKEN, parse_mode='HTML')
        dp = Dispatcher(fsm_strategy=FSMStrategy.USER_IN_CHAT, storage=MemoryStorage()) 
    except:
        logger.error('couldnt connect to telegram api')
    logger.info('Bot started')

    dp.update.middleware(InjectDBContextMiddleware())

    dp.include_router(AddressRouter().router)
    dp.include_router(CartRouter().router)
    dp.include_router(CatalogRouter().router)
    dp.include_router(MenuRouter(admin_chat_id=ADMIN_CHAT_ID).router)
    dp.include_router(OrderRouter().router)
    dp.include_router(PurchaseRouter().router)
    dp.include_router(SearchRouter().router)
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main(), debug=True)

