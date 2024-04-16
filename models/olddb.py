from os import getenv
import asyncio
import logging

from models.dao import ItemDAO, OrderDAO, OrderItemDAO, CartItemDAO, AddressDAO

import psycopg
from psycopg.rows import class_row
from psycopg.rows import dict_row
from dotenv import load_dotenv
from aiogram.types import FSInputFile

load_dotenv()
DATABASE = getenv('DATABASE')
ADMIN = getenv('ADMIN_CHAT_ID')

def log_query(query : str) -> None:
    info = "Query to DATABASE:"
    for i in query.split('\n'):
        info += ('\n\t' + i)
    logging.info(info)    

def log_query_result(result) -> None:
    res = ''
    if result is None:
        res ='None results'
    elif type(result) == list:
        res = str(len(result)) + 'results'
    else:
        res = f'1 {type(result)} result: \n {result}'
    info = f'Query returned {res}'
    logging.info(info)

class ItemsTable:
    async def connect(self):
        self.conn = await psycopg.AsyncConnection.connect(DATABASE,
                                                           autocommit=True)

    async def get_categories(self, page : int) -> list[str]:
        categories = ["Ремонтные составы", "Смеси для пола", "Клеящий состав",
                       "Штукатурка ", "Лакокрасочные материалы", "Затирка",
                         "Грунт", "Пропитки, добавки, пластификаторы",
                           "Шпаклевка", "Инструменты", "Изоляция"]
        cursor = (page-1)*4
        return categories[cursor: cursor + 4] 

    def add_amount(self, id : int, amount : int) -> None:
        return
    
    def subtract_amount(self, id : int, amount : int) -> None:
        return
    
    async def get_all(self) -> list[ItemDAO]:
        query = f'select * from items'
        log_query(query)
        async with self.conn.cursor(row_factory=class_row(ItemDAO)) as cur:
            await cur.execute(query)
            result = await cur.fetchall()
            log_query_result(result)
            return result
    
    async def get_by_category(self, category : str) -> list[ItemDAO]:
        query = f"select * from items where group_name = '{category}'"
        log_query(query)
        async with self.conn.cursor(row_factory=class_row(ItemDAO)) as cur:
            await cur.execute(query)
            result = await cur.fetchall()
            log_query_result(result)
            return result
    
    async def get_by_id(self, item_id : int) -> ItemDAO:
        query = f"select * from items where id = '{item_id}'"
        log_query(query)
        async with self.conn.cursor(row_factory=class_row(ItemDAO)) as cur:
            await cur.execute(query)
            result = await cur.fetchone()
            log_query_result(result)
            return result
    
    async def get_names(self) -> list[dict]:
        return
    
    async def find(self, query : str) -> list[ItemDAO] | None:
        query = f"select * from items where to_tsvector(lower(name)) 
        @@ plainto_tsquery(lower('{query}'))"
        log_query(query)
        async with self.conn.cursor(row_factory=class_row(ItemDAO)) as cur:
            await cur.execute(query)
            result = await cur.fetchall()
            log_query_result(result)
            return result


class AddressesTable:
    async def connect(self):
        self.conn = await psycopg.AsyncConnection.connect(DATABASE, 
                                                          autocommit=True)

    async def get_by_user_id(self, user_id : int) -> list[class_row]:
        query = f'select * from addresses where user_id = {user_id}'
        log_query(query)
        async with self.conn.cursor(row_factory=class_row(AddressDAO)) as cur:
            await cur.execute(query)
            result = await cur.fetchall()
            log_query_result(result)
            return result

    async def get_by_id(self, id : int) -> class_row:
        query = f'select * from addresses where id = {id}'
        log_query(query)
        async with self.conn.cursor(row_factory=class_row(AddressDAO)) as cur:
            await cur.execute(query)
            result = await cur.fetchone()
            log_query_result(result)
            return result

    async def delete_by_user_id(self, user_id : int):
        query = f'delete from addresses where user_id = {user_id}'
        log_query(query)
        async with self.conn.cursor(row_factory=class_row(AddressDAO)) as cur:
            await cur.execute(query)

    async def delete_by_id(self, id : int):
        query = f'delete from addresses where id = {id}'
        log_query(query)
        async with self.conn.cursor(row_factory=class_row(AddressDAO)) as cur:
            await cur.execute(query)

    async def add(self,user_id :int = 0,index : str = '',country : str = '',
                  city : str = '',street : str = '',house : str = '',
                  building : str = '',office : str = ''):
        query = f"insert into addresses (user_id, index, country, city, street, 
                    house, building, office) values({user_id}, '{index}', 
                        '{country}', '{city}', '{street}', '{house}', 
                            '{building}', '{office}')" 
        log_query(query)
        async with self.conn.cursor(row_factory=class_row(AddressDAO)) as cur:
            await cur.execute(query)
            
class OrdersTable:
    async def connect(self):
        return
        
    async def add(self, order : OrderDAO) -> int:
        return
        
    async def get_all(self, status : str = '') -> list[OrderDAO]:
        return
        

class ImagesTable:
    async def connect(self):
        self.conn = await psycopg.AsyncConnection.connect(DATABASE, 
                                                          autocommit=True)

    async def add(self, file_id : str, file_name : str) -> None:
        query = f"insert into images (file_id, file_name) values 
                ('{file_id}', '{file_name}')"
        log_query(query)
        async with self.conn.cursor() as cur:
            await cur.execute(query)
    
    async def get_all(self) -> list[dict]:
        query = f"select (file_name, file_id) from images"
        log_query(query)
        async with self.conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(query)
            result = await cur.fetchall()
            log_query_result(result)
            return result

    async def delete(self, id : int) -> None:
        query = f"delete from sklad where id = {id}"
        log_query(query)
        async with self.conn.cursor() as cur:
            await cur.execute(query)
    
    async def get_by_name(self, file_name : str) -> str:
        query = f"select file_id from images where file_name = '{file_name}' "
        log_query(query)
        async with self.conn.cursor() as cur:
            await cur.execute(query)
            result = (await cur.fetchone())[0]
            log_query_result(result)
            return result
        
    async def upload_(self, bot):
        query = f'select image from items'
        log_query(query)
        async with self.conn.cursor() as cur:
            await cur.execute(query)
            images = await cur.fetchall()
            for im in images:
                name = im[0]
                if name == '': 
                    continue
                await cur.execute(f"select file_id from images where 
                                file_name = '{name}'")
                res = (await cur.fetchone())
                if res is None:
                    photo = FSInputFile(path = rel + name)
                    message = await bot.send_photo(chat_id=ADMIN, caption=name, 
                                                   photo=photo)
                    await cur.execute(f"insert into images (file_id, file_name) 
                                      values ('{message.photo[0].file_id}', 
                                        '{name}')")

        

class OrderedItemsTable:
    async def connect(self):
        return
        
    async def add_cart(self, cart : list[OrderItemDAO], order_id : int) -> None:
        return
        
    async def get_by_order_id(self, order_id : int) -> list[OrderItemDAO]:
        return
        
class CartsTable:

    async def connect(self):
        self.conn = await psycopg.AsyncConnection.connect(DATABASE, 
                                                          autocommit=True)

    async def add_to_cart(self, user_id : int | str, item_id : str, 
                          amount : int) -> list[CartItemDAO]:
        async with self.conn.cursor(row_factory=class_row(CartItemDAO)) as cur:
            que1 = "select amount from carts where user_id = %s and \
                    item_id = '%s'"%(user_id, item_id)
            await cur.execute(que1)
            current_amnt = await cur.fetchone()
            log_query_result(current_amnt)
            if current_amnt:
                que2 = "update carts set amount = %s where user_id = %s and \
                        item_id = '%s'"%(amount + current_amnt, user_id, item_id)
                log_query(que2)
                await cur.execute(que2)
            else:
                que3= "insert into carts(user_id, item_id, amount) \
                        values(%s, '%s', %s)"%(user_id, item_id, amount)
                log_query(que3)
                await cur.execute(que3)
            
            que4 = 'select * from carts where user_id = %s '%user_id
            log_query(que4)
            await cur.execute(que4)
            result = await cur.fetchall()
            return result

    async def set_amount(self, user_id : int | str, item_id : int | str, 
                         amount : int) -> list[CartItemDAO]:
        async with self.conn.cursor(row_factory=class_row(CartItemDAO)) as cur:
            if amount <= 0:
                query = "delete from carts where user_id = %s and \
                        item_id = '%s'"%(user_id, item_id)
                log_query(query)
                await cur.execute(query)
            else:
                query = "update carts set amount = %s where user_id = %s and \
                        item_id = '%s'"%(amount, user_id, item_id)
                log_query(query)
                await cur.execute(query)
            query = 'select * from carts where user_id = %s '%user_id
            log_query(query)
            await cur.execute(query)
            result = await cur.fetchall()
            log_query_result(result)
            return result
            

    async def get_cart(self, user_id : int | str) -> list[CartItemDAO]:
        query = f"select * from carts where user_id = {user_id}"
        log_query(f"select * from carts where user_id = {user_id}")
        async with self.conn.cursor(row_factory=class_row(CartItemDAO)) as cur:
            await cur.execute(query)
            result = await cur.fetchall()
            log_query_result(result)
            return result
    
    async def get_amount(self, user_id, item_id) -> int:
        query = "select amount from carts where user_id = %s and \
                items_id = %s"%(user_id, item_id)
        log_query("select amount from carts where user_id = %s and \
                items_id = %s"%(user_id, item_id))
        async with self.conn.cursor() as cur:
            await cur.execute(query)
            result = (await cur.fetchone())[0]
            log_query_result(result)
            return result

    async def remove_item(self, user_id : int | str, 
                          item_id : int | str) -> list[CartItemDAO]:
        query = "delete from carts where user_id = %s and \
                item_id = '%s'"%(user_id, item_id)
        log_query("delete from carts where user_id = %s and \
                item_id = '%s'"%(user_id, item_id))
        async with self.conn.cursor() as cur:
            await cur.execute(query)
            await cur.execute('select * from carts where user_id = %s '%user_id)
            result = await cur.fetchall()
            log_query_result(result)
            return result

    async def clear_cart(self, user_id : int | str) -> None:
        query = "delete from carts where user_id = %s"%(user_id)
        log_query("delete from carts where user_id = %s"%(user_id))
        async with self.conn.cursor() as cur:
            await cur.execute(query)

        
class DataBase:
    async def connect(self):
        return
        
    async def execute(self, command: str, *args,
                      fetch: bool = False,
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      execute: bool = False):
        return
        
async def connect():
    await items_tab.connect()
    await orders_tab.connect()
    await ordered_items_tab.connect()
    await addresses_tab.connect()
    await images_tab.connect()
    await cart_tab.connect()

items_tab = ItemsTable()
orders_tab = OrdersTable()
ordered_items_tab = OrderedItemsTable()
images_tab = ImagesTable()
addresses_tab = AddressesTable()
cart_tab = CartsTable()

asyncio.run(connect())

