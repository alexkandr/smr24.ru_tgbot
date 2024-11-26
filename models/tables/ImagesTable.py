from psycopg.rows import class_row, dict_row
from models.dao import ItemDAO, OrderDAO, OrderItemDAO, CartItemDAO, AddressDAO, GroupDao
from models.db import DataBase

class ImagesTable:

    def __init__(self):
        self.db = DataBase()

    async def add(self, file_id : str, file_name : str) -> None:
        query = f"insert into images (file_id, file_name) values \
                ('{file_id}', '{file_name}')"
        
        await self.db.execute(query, fetch=False)
    
    async def get_all(self) -> list[dict]:
        query = f"select (file_name, file_id) from images"
        
        result = await self.db.execute(command=query, factory=dict_row(), fetch=True)
        return result

    async def delete(self, id : int) -> None:
        query = f"delete from sklad where id = {id}"
        
        await self.db.execute(query, fetch=False)
    
    async def get_by_name(self, file_name : str) -> str:
        query = f"select file_id from images where file_name = '{file_name}' "
        
        result = (await self.db.execute(query, fetch=True))[0][0]
        return result