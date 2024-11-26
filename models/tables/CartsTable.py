from psycopg.rows import class_row, dict_row
from models.dao import ItemDAO, OrderDAO, OrderItemDAO, CartItemDAO, AddressDAO, GroupDao
from models.db import DataBase

class CartsTable:

    def __init__(self):
        self.db = DataBase()

    async def add_to_cart(self, user_id : int | str, item_id : str, 
                          amount : int) -> list[CartItemDAO]:
        
        que1 = "select amount from carts where user_id = %s and \
                    item_id = '%s'"%(user_id, item_id)
        current_amnt = (await self.db.execute(que1, 
                                        fetch=True))
        if current_amnt != []:
            que2 = "update carts set amount = %s where user_id = %s and \
                    item_id = '%s'"%(amount + current_amnt[0][0], user_id, item_id)
            await self.db.execute(que2)
        else:
            que3= "insert into carts(user_id, item_id, amount) \
                    values(%s, '%s', %s)"%(user_id, item_id, amount)
            await self.db.execute(que3)
            
        que4 = 'select * from carts where user_id = %s '%user_id
        result = await self.db.execute(que4, factory=class_row(CartItemDAO), 
                                  fetch=True)
        return result

    async def set_amount(self, user_id : int | str, item_id : int | str, 
                         amount : int) -> list[CartItemDAO]:
        
        if amount <= 0:
            query = "delete from carts where user_id = %s and \
                    item_id = '%s'"%(user_id, item_id)
            await self.db.execute(query)
        else:
            query = "update carts set amount = %s where user_id = %s and \
                    item_id = '%s'"%(amount, user_id, item_id)
            await self.db.execute(query)
        query = 'select * from carts where user_id = %s '%user_id
        result = await self.db.execute(query, factory=class_row(CartItemDAO), 
                                  fetch=True)
        return result
            

    async def get_cart(self, user_id : int | str) -> list[CartItemDAO]:
        query = f"select * from carts where user_id = {user_id}"
        
        result = await self.db.execute(query, factory=class_row(CartItemDAO), 
                                  fetch=True)
        return result
    
    async def get_amount(self, user_id, item_id) -> int:
        query = "select amount from carts where user_id = %s and \
                items_id = %s"%(user_id, item_id)
        
        result = await self.db.execute(query, factory=class_row(CartItemDAO), 
                                  fetch=True)
        return result[0][0]

    async def remove_item(self, user_id : int | str, 
                          item_id : int | str) -> list[CartItemDAO]:
        query = "delete from carts where user_id = %s and \
                item_id = '%s'"%(user_id, item_id)
        
        await self.db.execute(query, fetch=False)
        
        query = 'select * from carts where user_id = %s '%user_id
        result = await self.db.execute(query, factory=class_row(CartItemDAO), fetch=True)

    async def clear_cart(self, user_id : int | str) -> None:
        query = "delete from carts where user_id = %s"%(user_id)
        
        await self.db.execute(query, fetch=False)
