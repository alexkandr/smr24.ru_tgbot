from psycopg.rows import class_row, dict_row
from models.dao import ItemDAO, OrderDAO, OrderItemDAO, CartItemDAO, AddressDAO, GroupDao
from models.db import DataBase

class UsersTable:

    def __init__(self):
        self.db = DataBase()

    async def new_phone_number(self, phone_number : str, user_id : int):
        query = f'''update users set is_current = False where user_id = {user_id};
        insert into users (user_id, phone_number, is_current) values({user_id}, '{phone_number}', True);'''
        await self.db.execute(query, fetch=False)