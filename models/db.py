from os import getenv
import asyncio
import logging
from models.dao import ItemDAO, OrderDAO, OrderItemDAO, CartItemDAO, AddressDAO

import psycopg
import psycopg_pool
from psycopg.rows import class_row, dict_row
from dotenv import load_dotenv
from aiogram.types import FSInputFile

load_dotenv()
DATABASE = getenv('DATABASE')
ADMIN = getenv('ADMIN_CHAT_ID')

class DataBase:
    pool = None

    async def connect(self):
        self.pool = psycopg_pool.AsyncConnectionPool(conninfo=DATABASE, min_size=4,
                                                      open = True)
        await self.pool.open()
        logging.info('db connected')
    
        
    async def execute(self, command: str, factory = None, fetch: bool = False ):
        pre_log_info = "Query to DATABASE:"
        for i in command.split('\n'):
            pre_log_info += ('\n\t' + i)
        logging.info(pre_log_info)
        
        async with self.pool.connection() as conn:
            logging.info('connection created')
            async with conn.cursor(row_factory=factory) as cursor:
                logging.info('cursor created')
                await cursor.execute(command)
                result = None
                if fetch == True:
                    result = await cursor.fetchall() 
                    if result is None:
                        post_log_info ='None results'
                    elif type(result) == list:
                        post_log_info = str(len(result)) + 'results'
                    else:
                        post_log_info = f'1 {type(result)} result: \n {result}'

                    post_log_info = 'Query returned ' + post_log_info
                    logging.info(post_log_info)


                return result
    
    async def close(self):
        await self.pool.close()

db = DataBase()

class ItemsTable:
    groups_dict = {
        0: "Ремонтные составы",
        1: "Смеси для пола",
        2: "Клеящий состав",
        3: "Штукатурка ",
        4: "Лакокрасочные материалы",
        5: "Затирка",
        6: "Грунт",
        7: "Пропитки, добавки, пластификаторы",
        8: "Шпаклевка",
    }

    async def connect(self):
        self.conn = await psycopg.AsyncConnection.connect(DATABASE, autocommit=True)

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
    async def get_by_category(self, category : str) -> list[ItemDAO]:
        query = f"select * from items where group_name = '{category}'"
        log_query(query)
        async with self.conn.cursor(row_factory=class_row(ItemDAO)) as cur:
            await cur.execute(query)
            result = await cur.fetchall()
            log_query_result(result)
            return result
    async def get_by_cat_man(self, category : str, manufacturer:str) -> list[ItemDAO]:
        if manufacturer == 'other':
            query = f"select * from items where group_name = '{category}' and manufacturer_name is null"
        else:
            query = f"select * from items where group_name = '{category}' and manufacturer_name='{manufacturer}'"
        log_query(query)
        async with self.conn.cursor(row_factory=class_row(ItemDAO)) as cur:
            await cur.execute(query)
            result = await cur.fetchall()
            log_query_result(result)
            return result
    
    async def get_manufacturers_by_category(self, category : str) -> list[str]:
        query = f"select distinct manufacturer_name from items where group_name = '{category}'"
        log_query(query)
        async with self.conn.cursor() as cur:
            await cur.execute(query)
            result = [i[0] for i in await cur.fetchall()]
            log_query_result(result)
            return result

    async def get_by_id(self, item_id : int) -> ItemDAO:
        query = f"select * from items where id = '{item_id}'"
        
        result = await db.execute(command=query, factory=class_row(ItemDAO),
                                  fetch=True)
        return result
    
    async def get_names(self) -> list[dict]:
        return
    
    async def find(self, query : str) -> list[ItemDAO] | None:
        query = f"select * from items where to_tsvector(lower(name)) \
        @@ plainto_tsquery(lower('{query}'))"
        
        result = await db.execute(command=query, factory=class_row(ItemDAO),
                                  fetch=True)
        return result


class AddressesTable:

    async def get_by_user_id(self, user_id : int) -> list[class_row]:
        query = f'select * from addresses where user_id = {user_id}'
        
        result = await db.execute(command=query, factory=class_row(AddressDAO),
                                  fetch=True)
        return result

    async def get_by_id(self, id : int) -> AddressDAO:
        query = f'select * from addresses where id = {id}'
        
        result = await db.execute(command=query, factory=class_row(AddressDAO),
                                  fetch=True)
        return result

    async def delete_by_user_id(self, user_id : int):
        query = f'delete from addresses where user_id = {user_id}'
        
        await db.execute(command=query, fetch=True)

    async def delete_by_id(self, id : int):
        query = f'delete from addresses where id = {id}'
        
        await db.execute(command=query, fetch=False)

    async def add(self,user_id :int = 0,index : str = '',country : str = '',
                  city : str = '',street : str = '',house : str = '',
                  building : str = '',office : str = ''):
        
        query = \
        f"insert into addresses (user_id, index, country, city, street, \
        house, building, office) values({user_id}, '{index}', '{country}', \
        '{city}', '{street}', '{house}', '{building}', '{office}')" 
        
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
        
        result = (await db.execute(query, fetch=True))[0]
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
        return result[0]

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
        

        
async def connect():
    await db.connect()

items_tab = ItemsTable()
orders_tab = OrdersTable()
ordered_items_tab = OrderedItemsTable()
images_tab = ImagesTable()
addresses_tab = AddressesTable()
cart_tab = CartsTable()

asyncio.run(connect())

