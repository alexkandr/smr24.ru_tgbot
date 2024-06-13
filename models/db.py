from os import getenv
import asyncio
import logging
from datetime import datetime
from models.dao import ItemDAO, OrderDAO, OrderItemDAO, CartItemDAO, AddressDAO

import psycopg_pool
from psycopg.rows import class_row, dict_row
from dotenv import load_dotenv

load_dotenv()
DATABASE = getenv('DATABASE')

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
        self.pool = psycopg_pool.AsyncNullConnectionPool(conninfo=conninfo)
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
    per_page = 7
    groups_dict = {
        0: "Ремонтные составы",
        1: "Смеси для пола",
        2: "Клеящий состав",
        3: "Затирка",
        4: "Шпаклевка",
        5: "Штукатурка ",
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
        query = f"select distinct manufacturer_name from items where group_name = '{category}' and visible = True"
        result = await db.execute(command=query,
                                  fetch=True)
        return [r[0] for r in result]
    
    async def get_by_cat_man(self, category : str, manufacturer:str, page : int, avaible_only : bool = False) -> list[ItemDAO]:
        
        offset = (page-1)*self.per_page
        if manufacturer == 'other':
            query = f"select * from items where group_name = '{category}' and manufacturer_name is null and visible = True"
        else:
            if avaible_only:
                            query = f"select * from items where group_name = '{category}' and manufacturer_name='{manufacturer}' and visible = True and avaible > 0 limit {self.per_page} offset {offset}"
            else:
                query = f"select * from items where group_name = '{category}' and manufacturer_name='{manufacturer}' and visible = True limit {self.per_page} offset {offset}"
        
        result = await db.execute(command=query, factory=class_row(ItemDAO),
                                  fetch=True)
        count_que = f"select count(*) from items where group_name = '{category}' and manufacturer_name='{manufacturer}' and visible = True"
        count = await db.execute(command=count_que,
                                  fetch=True)        
        count = int(count[0][0])
        return result, count

    async def get_by_category(self, category : str) -> list[ItemDAO]:
        query = f"select * from items where group_name = '{category}' and visible = True"
        
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
    
    async def find(self, search : str, page : int, data_len : int=0) -> list[ItemDAO] | None:
        offset = (page -1)*self.per_page
        query = f"select * from items where to_tsvector(lower(name)) \
        @@ plainto_tsquery(lower('{search}')) and visible = True limit {self.per_page} offset {offset}"
        
        result = await db.execute(command=query, factory=class_row(ItemDAO),
                                  fetch=True)
        count_que  = f"select count(*) from items where to_tsvector(lower(name)) \
        @@ plainto_tsquery(lower('{search}')) and visible = True"
        count = data_len if data_len > 0 else int((await db.execute(command=count_que, fetch=True))[0][0])
        return result, count


class AddressesTable:

    async def get_by_user_id(self, user_id : int, visible_only :bool = True) -> list[class_row]:
        if visible_only:
            query = f'select id, user_id, index, country, city, street, house, building, office, visible from addresses where user_id = {user_id} and visible = True'
        else:
            query = f'select id, user_id, index, country, city, street, house, building, office, visible from addresses where user_id = {user_id}'
        
        result = await db.execute(command=query, factory=class_row(AddressDAO),
                                  fetch=True)
        return result

    async def get_by_id(self, id : int) -> AddressDAO:
        query = f'select id, user_id, index, country, city, street, house, building, office, visible from addresses where id = {id}'
        
        result = await db.execute(command=query, factory=class_row(AddressDAO),
                                  fetch=True)
        return result[0]
    
    async def get_takeaway_addresses(self) -> list[AddressDAO]:
        query = f'select id, user_id, index, country, city, street, house, building, office, visible from addresses where is_takeaway = true and visible = true'
        result = await db.execute(command=query, factory=class_row(AddressDAO),
                                  fetch=True)
        return result
    async def check_is_takeaway(self, id) -> bool:
        query = f'select is_takeaway from addresses where id = {id}'
        result = await db.execute(command=query, 
                                  fetch=True)
        return result[0][0]
    
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
        house, building, office, visible, is_takeaway) values({user_id}, '{index}', '{country}', \
        '{city}', '{street}', '{house}', '{building}', '{office}', '{visible}', False)" 
        
        await db.execute(command=query, fetch=False)
            
class OrdersTable:

    async def add(self, order : OrderDAO) -> str:
        order.id = 'b_' + str(abs(hash(datetime.now())))
        order.creating_time = datetime.now()
        values = list(order.values_as_tuple())
        
        query = "insert into orders (id, user_id, address_id, total_sum, \
            payment_method, status, payment_status, creating_time, is_takeaway) values \
                ('{}', {}, {}, {}, '{}', '{}', '{}', '{}', {})".format(order.id, *values)
        
        await db.execute(query, fetch=False)
        return order.id
        
    async def get_all(self, status : str = '') -> list[OrderDAO]:
        if status == '':
            query = 'select * from orders'
        else:
            query = f"select * from orders where status = '{status}'"
        return (await db.execute(query, class_row(OrderDAO), fetch=True))
        
    async def get_by_user_id(self, user_id : str = '', status='') -> list[OrderDAO]:
        query = f"select * from orders where user_id = {user_id}" 
        return (await db.execute(query, class_row(OrderDAO), fetch=True))
    
    async def get_by_id(self, order_id : str = '', status='') -> OrderDAO:
        query = f"select * from orders where id = '{order_id}'" 
        return (await db.execute(query, class_row(OrderDAO), fetch=True))[0]
    
    async def update_status(self, order_id : str = '', status='', payment_status :str = '') -> OrderDAO:
        query = f"update orders set status = '{status}', payment_status = '{payment_status}' where id = '{order_id}'" 
        await db.execute(query)
    
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
         
    async def add_item(self, item_id : str, order_id: str, amount :float) -> None:
        query=f"insert into ordered_items (item_id, order_id, amount) values\
            ('{item_id}', '{order_id}', {amount})"
        await db.execute(query, fetch=False)
        
    async def get_by_order_id(self, order_id : int) -> list[OrderItemDAO]:
        query = f"select * from ordered_items where order_id = '{order_id}'"
        result = await db.execute(query, class_row(OrderItemDAO), fetch=True)
        return result
        
class CartsTable:

    async def add_to_cart(self, user_id : int | str, item_id : str, 
                          amount : int) -> list[CartItemDAO]:
        
        que1 = "select amount from carts where user_id = %s and \
                    item_id = '%s'"%(user_id, item_id)
        current_amnt = (await db.execute(que1, 
                                        fetch=True))
        if current_amnt != []:
            que2 = "update carts set amount = %s where user_id = %s and \
                    item_id = '%s'"%(amount + current_amnt[0][0], user_id, item_id)
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
    logging.getLogger("psycopg.pool").setLevel(logging.INFO)
    await db.connect()

items = ItemsTable()
orders = OrdersTable()
ordered_items = OrderedItemsTable()
images = ImagesTable()
addresses = AddressesTable()
carts = CartsTable()

asyncio.run(connect())

