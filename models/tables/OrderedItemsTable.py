from psycopg.rows import class_row, dict_row
from models.dao import ItemDAO, OrderDAO, OrderItemDAO, CartItemDAO, AddressDAO, GroupDao
from models.db import DataBase

class OrderedItemsTable:
         
    def __init__(self):
        self.db = DataBase()
        
    async def add_item(self, item_id : str, order_id: str, amount :float) -> None:
        query=f"insert into ordered_items (item_id, order_id, amount) values\
            ('{item_id}', '{order_id}', {amount})"
        await self.db.execute(query, fetch=False)
        
    async def get_by_order_id(self, order_id : int) -> list[OrderItemDAO]:
        query = f"select * from ordered_items where order_id = '{order_id}'"
        result = await self.db.execute(query, class_row(OrderItemDAO), fetch=True)
        return result