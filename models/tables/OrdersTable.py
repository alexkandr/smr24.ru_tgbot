from datetime import datetime
from psycopg.rows import class_row, dict_row
from models.dao import ItemDAO, OrderDAO, OrderItemDAO, CartItemDAO, AddressDAO, GroupDao
from models.db import DataBase

class OrdersTable:
    
    def __init__(self):
        self.db = DataBase()
        
    async def add(self, order : OrderDAO) -> str:
        order.id = 'b_' + str(abs(hash(datetime.now())))
        order.creating_time = datetime.now()
        values = list(order.values_as_tuple())
        
        query = "insert into orders (id, user_id, address_id, total_sum, \
            payment_method, status, payment_status, creating_time, is_takeaway) values \
                ('{}', {}, {}, {}, '{}', '{}', '{}', '{}', {})".format(order.id, *values)
        
        await self.db.execute(query, fetch=False)
        return order.id
        
    async def get_all(self, status : str = '') -> list[OrderDAO]:
        if status == '':
            query = 'select * from orders'
        else:
            query = f"select * from orders where status = '{status}'"
        return (await self.db.execute(query, class_row(OrderDAO), fetch=True))
        
    async def get_by_user_id(self, user_id : str = '', status='') -> list[OrderDAO]:
        query = f"select * from orders where user_id = {user_id}" 
        return (await self.db.execute(query, class_row(OrderDAO), fetch=True))
    
    async def get_by_id(self, order_id : str = '', status='') -> OrderDAO:
        query = f"select * from orders where id = '{order_id}'" 
        return (await self.db.execute(query, class_row(OrderDAO), fetch=True))[0]
    
    async def update_status(self, order_id : str = '', status='', payment_status :str = '') -> OrderDAO:
        query = f"update orders set status = '{status}', payment_status = '{payment_status}' where id = '{order_id}'" 
        await self.db.execute(query)