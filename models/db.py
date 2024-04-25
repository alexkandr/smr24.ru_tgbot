from os import getenv
import asyncio
import logging
from models.dao import ItemDAO, OrderDAO, OrderItemDAO, CartItemDAO, AddressDAO

import psycopg_pool
from psycopg.rows import class_row, dict_row
from dotenv import load_dotenv
from aiogram.types import FSInputFile

load_dotenv()
DATABASE = getenv('DATABASE')
ADMIN = getenv('ADMIN_CHAT_ID')
logging.getLogger("psycopg.pool").setLevel(logging.INFO)

class DataBase:

    def __init__(self, logger_name = __name__) -> None:
        self.logger = logging.getLogger(logger_name)

    async def connect(self, conninfo = DATABASE):
        """
    establishes connection to db
    
    Parameters
    ----------
    conninfo : connection string
    
    Returns
    ------- 
    None
        """
        self.logger.info('Establishing database connection')
        self.pool = psycopg_pool.AsyncConnectionPool(conninfo=conninfo, min_size=4, max_size=10, max_waiting=5)
        self.logger.info('db connected')
        await self.pool.open()
        await self.pool.wait()
        self.logger.info('pool opened')
    
        
    async def execute(self, command: str, factory = None, fetch: bool = False ):
        """
executes command to connected db

Parameters
----------
command : query to db
factory : row_factory for cursor
fetch : true if execution should return result of quer

Returns
------- 
None if fetch == False, else list of results. List of tuples if factory is None
        """
        pre_log_info = "Query to DATABASE:"
        for i in command.split('\n'):
            pre_log_info += ('\n\t' + i)
        self.logger.info(pre_log_info)
        

        async with self.pool.connection() as conn:
            self.logger.info(f'connection created \n Currently avaible {self.pool.get_stats()["pool_available"]} connections')
            
            async with conn.cursor(row_factory=factory) as cursor:
                await cursor.execute(command)
                result = None
                if fetch == True:
                    result = await cursor.fetchall() 
                    res_len=len(result)
                    if res_len !=1 :
                        post_log_info = f'list of {res_len} {type(result[0]) if res_len != 0 else "None"}'
                    else:
                        post_log_info = f'1 {type(result[0])} result: \n {result}'

                    post_log_info = 'Query returned ' + post_log_info
                    self.logger.info(post_log_info)


        return result
    
    async def close(self):
        await self.pool.close()

class ItemsTable:
    groups_dict = {
        0: "Ремонтные составы",
        1: "Смеси для пола",
        2: "Клеящий состав",
        3: "Затирка",
        4: "Шпаклевка",
        5: "Штукатурка",
        6: "Грунт",
        7: "Пропитки, добавки, пластификаторы",
        8: "Лакокрасочные материалы",
    }

    async def get_categories(self, page : int) -> list[str]:
        categories = range(0,9)
        cursor = (page-1)*4
        return categories[cursor: cursor + 4] 

    def add_amount(self, id : int, amount : int) -> None:
        return
    
    def subtract_amount(self, id : int, amount : int) -> None:
        return
    
    async def get_all(self) -> list[ItemDAO]:
        query = f'select * from items'
        
        result = await db.execute(command=query, factory=class_row(ItemDAO),
                                  fetch=True)
        return result    
    
    async def get_manufacturers_by_category(self, category : str) -> list[str]:
        query = f"select distinct manufacturer_name from items where group_name = '{category}'"
        result = await db.execute(command=query,
                                  fetch=True)
        return [r[0] for r in result]
    
    async def get_by_cat_man(self, category : str, manufacturer:str) -> list[ItemDAO]:
        if manufacturer == 'other':
            query = f"select * from items where group_name = '{category}' and manufacturer_name is null"
        else:
            query = f"select * from items where group_name = '{category}' and manufacturer_name='{manufacturer}'"
        
        result = await db.execute(command=query, factory=class_row(ItemDAO),
                                  fetch=True)
        return result    

    async def get_by_category(self, category : str) -> list[ItemDAO]:
        query = f"select * from items where group_name = '{category}'"
        
        result = await db.execute(command=query, factory=class_row(ItemDAO),
                                  fetch=True)
        return result
    
    async def get_by_id(self, item_id : int) -> ItemDAO:
        query = f"select * from items where id = '{item_id}'"
        
        result = await db.execute(command=query, factory=class_row(ItemDAO),
                                  fetch=True)
        return result[0]
    
    async def get_names(self) -> list[dict]:
        return
    
    async def find(self, query : str) -> list[ItemDAO] | None:
        query = f"select * from items where to_tsvector(lower(name)) \
        @@ plainto_tsquery(lower('{query}'))"
        
        result = await db.execute(command=query, factory=class_row(ItemDAO),
                                  fetch=True)
        return result


class AddressesTable:

    async def get_by_user_id(self, user_id : int, visible_only :bool = True) -> list[class_row]:
        if visible_only:
            query = f'select * from addresses where user_id = {user_id} and visible = True'
        else:
            query = f'select * from addresses where user_id = {user_id}'
        
        result = await db.execute(command=query, factory=class_row(AddressDAO),
                                  fetch=True)
        return result

    async def get_by_id(self, id : int) -> AddressDAO:
        query = f'select * from addresses where id = {id}'
        
        result = await db.execute(command=query, factory=class_row(AddressDAO),
                                  fetch=True)
        return result[0]

    async def delete_by_user_id(self, user_id : int):
        query = f'update addresses set visible = false where user_id = {user_id}'
        
        await db.execute(command=query, fetch=True)

    async def delete_by_id(self, id : int):
        query = f'update addresses set visible = false where id = {id}'
        
        await db.execute(command=query, fetch=False)

    async def add(self,user_id :int = 0,index : str = '',country : str = '',
                  city : str = '',street : str = '',house : str = '',
                  building : str = '',office : str = '', visible=True):
        
        query = \
        f"insert into addresses (user_id, index, country, city, street, \
        house, building, office, visible) values({user_id}, '{index}', '{country}', \
        '{city}', '{street}', '{house}', '{building}', '{office}', '{visible}')" 
        
        await db.execute(command=query, fetch=False)
            
class OrdersTable:

    async def add(self, order : OrderDAO) -> int:
        return
        
    async def get_all(self, status : str = '') -> list[OrderDAO]:
        return
        

class ImagesTable:

    async def add(self, file_id : str, file_name : str) -> None:
        query = f"insert into images (file_id, file_name) values \
                ('{file_id}', '{file_name}')"
        
        await db.execute(query, fetch=False)
    
    async def get_all(self) -> list[dict]:
        query = f"select (file_name, file_id) from images"
        
        result = await db.execute(command=query, factory=dict_row(), fetch=True)
        return result

    async def delete(self, id : int) -> None:
        query = f"delete from sklad where id = {id}"
        
        await db.execute(query, fetch=False)
    
    async def get_by_name(self, file_name : str) -> str:
        query = f"select file_id from images where file_name = '{file_name}' "
        
        result = (await db.execute(query, fetch=True))[0][0]
        return result
        

class OrderedItemsTable:
        
    async def add_cart(self, cart : list[OrderItemDAO], order_id : int) -> None:
        return
        
    async def get_by_order_id(self, order_id : int) -> list[OrderItemDAO]:
        return
        
class CartsTable:

    async def add_to_cart(self, user_id : int | str, item_id : str, 
                          amount : int) -> list[CartItemDAO]:
        
        que1 = "select amount from carts where user_id = %s and \
                    item_id = '%s'"%(user_id, item_id)
        current_amnt = await db.execute(que1, factory=class_row(CartItemDAO), 
                                        fetch=True)
        if current_amnt:
            que2 = "update carts set amount = %s where user_id = %s and \
                    item_id = '%s'"%(amount + current_amnt, user_id, item_id)
            await db.execute(que2)
        else:
            que3= "insert into carts(user_id, item_id, amount) \
                    values(%s, '%s', %s)"%(user_id, item_id, amount)
            await db.execute(que3)
            
        que4 = 'select * from carts where user_id = %s '%user_id
        result = await db.execute(que4, factory=class_row(CartItemDAO), 
                                  fetch=True)
        return result

    async def set_amount(self, user_id : int | str, item_id : int | str, 
                         amount : int) -> list[CartItemDAO]:
        
        if amount <= 0:
            query = "delete from carts where user_id = %s and \
                    item_id = '%s'"%(user_id, item_id)
            await db.execute(query)
        else:
            query = "update carts set amount = %s where user_id = %s and \
                    item_id = '%s'"%(amount, user_id, item_id)
            await db.execute(query)
        query = 'select * from carts where user_id = %s '%user_id
        result = await db.execute(query, factory=class_row(CartItemDAO), 
                                  fetch=True)
        return result
            

    async def get_cart(self, user_id : int | str) -> list[CartItemDAO]:
        query = f"select * from carts where user_id = {user_id}"
        
        result = await db.execute(query, factory=class_row(CartItemDAO), 
                                  fetch=True)
        return result
    
    async def get_amount(self, user_id, item_id) -> int:
        query = "select amount from carts where user_id = %s and \
                items_id = %s"%(user_id, item_id)
        
        result = await db.execute(query, factory=class_row(CartItemDAO), 
                                  fetch=True)
        return result[0][0]

    async def remove_item(self, user_id : int | str, 
                          item_id : int | str) -> list[CartItemDAO]:
        query = "delete from carts where user_id = %s and \
                item_id = '%s'"%(user_id, item_id)
        
        await db.execute(query, fetch=False)
        
        query = 'select * from carts where user_id = %s '%user_id
        result = await db.execute(query, factory=class_row(CartItemDAO), fetch=True)

    async def clear_cart(self, user_id : int | str) -> None:
        query = "delete from carts where user_id = %s"%(user_id)
        
        await db.execute(query, fetch=False)
        

        
db = DataBase(logger_name='MainPgDB')
async def connect():
    await db.connect()

items = ItemsTable()
orders = OrdersTable()
ordered_items = OrderedItemsTable()
images = ImagesTable()
addresses = AddressesTable()
carts = CartsTable()

asyncio.run(connect())

