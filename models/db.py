from os import getenv
import asyncio

from models.dao import ItemDAO, OrderDAO, OrderItemDAO, CartItemDAO, AddressDAO

import psycopg
from psycopg.rows import class_row
from psycopg.rows import dict_row
from dotenv import load_dotenv
from aiogram.types import FSInputFile

load_dotenv()
DATABASE = getenv('DATABASE')
ADMIN = getenv('ADMIN_CHAT_ID')

class ItemsTable:
    async def connect(self):
        self.conn = await psycopg.AsyncConnection.connect(DATABASE, autocommit=True)

    async def get_categories(self, page : int) -> list[str]:
        categories = ["Ремонтные составы", "Смеси для пола", "Клеящий состав", "Штукатурка ", "Лакокрасочные материалы", "Затирка", "Грунт", "Пропитки, добавки, пластификаторы", "Шпаклевка", "Инструменты", "Изоляция"]
        cursor = (page-1)*4
        return categories[cursor: cursor + 4] 

    def add_amount(self, id : int, amount : int) -> None:
        return
    
    def subtract_amount(self, id : int, amount : int) -> None:
        return
    
    async def get_all(self) -> list[ItemDAO]:
        async with self.conn.cursor(row_factory=class_row(ItemDAO)) as cur:
            await cur.execute(f'select * from items')
            return await cur.fetchall()
    
    async def get_by_category(self, category : str) -> list[ItemDAO]:
        async with self.conn.cursor(row_factory=class_row(ItemDAO)) as cur:
            await cur.execute(f"select * from items where group_name = '{category}'")
            return await cur.fetchall()
    
    async def get_by_id(self, item_id : int) -> ItemDAO:
        async with self.conn.cursor(row_factory=class_row(ItemDAO)) as cur:
            await cur.execute(f"select * from items where id = '{item_id}'")
            return await cur.fetchone()
    
    async def get_names(self) -> list[dict]:
        return
    async def find(self, query : str) -> list[ItemDAO] | None:
        async with self.conn.cursor(row_factory=class_row(ItemDAO)) as cur:
            await cur.execute(f"select * from items where to_tsvector(lower(name)) @@ plainto_tsquery(lower('{query}'))")
            return await cur.fetchall()


class AddressesTable:
    async def connect(self):
        self.conn = await psycopg.AsyncConnection.connect(DATABASE, autocommit=True)

    async def get_by_user_id(self, user_id : int) -> list[class_row]:
        async with self.conn.cursor(row_factory=class_row(AddressDAO)) as cur:
            await cur.execute(f'select * from addresses where user_id = {user_id}')
            return await cur.fetchall()

    async def get_by_id(self, id : int) -> class_row:
        async with self.conn.cursor(row_factory=class_row(AddressDAO)) as cur:
            await cur.execute(f'select * from addresses where id = {id}')
            return await cur.fetchone()

    async def delete_by_user_id(self, user_id : int):
        async with self.conn.cursor(row_factory=class_row(AddressDAO)) as cur:
            await cur.execute(f'delete from addresses where user_id = {user_id}')

    async def delete_by_id(self, id : int):
        async with self.conn.cursor(row_factory=class_row(AddressDAO)) as cur:
            await cur.execute(f'delete from addresses where id = {id}')

    async def add(self,user_id :int = 0,index : str = '',country : str = '',city : str = '',street : str = '',house : str = '',building : str = '',office : str = ''):
        async with self.conn.cursor(row_factory=class_row(AddressDAO)) as cur:
            await cur.execute(f"insert into addresses (user_id, index, country, city, street, house, building, office) values({user_id}, '{index}', '{country}', '{city}', '{street}', '{house}', '{building}', '{office}')")        
            
class OrdersTable:
    async def connect(self):
        return
        
    async def add(self, order : OrderDAO) -> int:
        return
        
    async def get_all(self, status : str = '') -> list[OrderDAO]:
        return
        

class ImagesTable:
    async def connect(self):
        self.conn = await psycopg.AsyncConnection.connect(DATABASE, autocommit=True)

    async def add(self, file_id : str, file_name : str) -> None:
        async with self.conn.cursor() as cur:
            await cur.execute(f"insert into images (file_id, file_name) values ('{file_id}', '{file_name}')")
    
    async def get_all(self) -> list[dict]:
        async with self.conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(f"select (file_name, file_id) from images")
            return await cur.fetchall()

    async def delete(self, id : int) -> None:
        async with self.conn.cursor() as cur:
            await cur.execute(f"delete from sklad where id = {id}")
    
    async def get_by_name(self, file_name : str) -> str:
        async with self.conn.cursor() as cur:
            await cur.execute(f"select file_id from images where file_name = '{file_name}' ")
            return (await cur.fetchone())[0]
        
    async def upload_(self, bot):
        async with self.conn.cursor() as cur:
            await cur.execute(f'select image from items')
            images = await cur.fetchall()
            for im in images:
                name = im[0]
                if name == '': 
                    continue
                await cur.execute(f"select file_id from images where file_name = '{name}'")
                res = (await cur.fetchone())
                if res is None:
                    photo = FSInputFile(path = '/Users/akant/Documents/dlyaDrugih/plumbermag/smr24.ru_tgbot/models/data/' + name)
                    message = await bot.send_photo(chat_id=ADMIN, caption=name, photo=photo)
                    await cur.execute(f"insert into images (file_id, file_name) values ('{message.photo[0].file_id}', '{name}')")

        

class OrderedItemsTable:
    async def connect(self):
        return
        
    async def add_cart(self, cart : list[OrderItemDAO], order_id : int) -> None:
        return
        
    async def get_by_order_id(self, order_id : int) -> list[OrderItemDAO]:
        return
        
class CartsTable:

    async def connect(self):
        self.conn = await psycopg.AsyncConnection.connect(DATABASE, autocommit=True)

    async def add_to_cart(self, user_id : int | str, item_id : int | str, amount : int) -> list[CartItemDAO]:
        async with self.conn.cursor(row_factory=class_row(CartItemDAO)) as cur:
            current_amnt = await (await cur.execute("select amount from carts where user_id = %s and item_id = '%s'"%(user_id, item_id))).fetchone()
            if current_amnt:
                await cur.execute("update carts set amount = %s where user_id = %s and item_id = '%s'"%(amount + current_amnt, user_id, item_id))
            else:
                await cur.execute("insert into carts(user_id, item_id, amount) values(%s, '%s', %s)"%(user_id, item_id, amount))
            return await (await cur.execute('select * from carts where user_id = %s '%user_id)).fetchall()

    async def set_amount(self, user_id : int | str, item_id : int | str, amount : int) -> list[CartItemDAO]:
        async with self.conn.cursor(row_factory=class_row(CartItemDAO)) as cur:
            if amount <= 0:
                await cur.execute("delete from cart where user_id = %s and item_id = '%s'"%(user_id, item_id))
            else:
                await cur.execute("update carts set amount = %s where user_id = %s and item_id = '%s'"%(amount, user_id, item_id))
            return await (await cur.execute('select * from carts where user_id = %s '%user_id)).fetchall()
            

    async def get_cart(self, user_id : int | str) -> list[CartItemDAO]:
        async with self.conn.cursor(row_factory=class_row(CartItemDAO)) as cur:
            await cur.execute(f"select * from carts where user_id = {user_id}")
            return await cur.fetchall()
    
    async def get_amount(self, user_id, item_id) -> int:
        async with self.conn.cursor() as cur:
            await cur.execute("select amount from carts where user_id = %s and items_id = %s"%(user_id, item_id))
            return (await cur.fetchone())[0]

    async def remove_item(self, user_id : int | str, item_id : int | str) -> list[CartItemDAO]:
        async with self.conn.cursor() as cur:
            await cur.execute("delete from carts where user_id = %s and item_id = '%s'"%(user_id, item_id))
            return await (await cur.execute('select * from carts where user_id = %s '%user_id)).fetchall()

    async def clear_cart(self, user_id : int | str) -> None:
        async with self.conn.cursor() as cur:
            await cur.execute("delete from carts where user_id = %s"%(user_id))

        
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

