from psycopg.rows import class_row
from models.dao import AddressDAO
from models.db import DataBase

class AddressesTable:

    def __init__(self):
        self.db = DataBase()

    async def get_by_user_id(self, user_id : int, is_visible_only :bool = True) -> list[class_row]:
        if is_visible_only:
            query = f'select id, user_id, index, country, city, street, house, building, office, is_visible from addresses where user_id = {user_id} and is_visible = True'
        else:
            query = f'select id, user_id, index, country, city, street, house, building, office, is_visible from addresses where user_id = {user_id}'
        
        result = await self.db.execute(command=query, factory=class_row(AddressDAO),
                                  fetch=True)
        return result

    async def get_by_id(self, id : int) -> AddressDAO:
        query = f'select id, user_id, index, country, city, street, house, building, office, is_visible from addresses where id = {id}'
        
        result = await self.db.execute(command=query, factory=class_row(AddressDAO),
                                  fetch=True)
        return result[0]
    
    async def get_takeaway_addresses(self) -> list[AddressDAO]:
        query = f'select id, user_id, index, country, city, street, house, building, office, is_visible from addresses where is_takeaway = true and is_visible = true'
        result = await self.db.execute(command=query, factory=class_row(AddressDAO),
                                  fetch=True)
        return result
    async def check_is_takeaway(self, id) -> bool:
        query = f'select is_takeaway from addresses where id = {id}'
        result = await self.db.execute(command=query, 
                                  fetch=True)
        return result[0][0]
    
    async def delete_by_user_id(self, user_id : int):
        query = f'update addresses set is_visible = false where user_id = {user_id}'
        
        await self.db.execute(command=query, fetch=True)

    async def delete_by_id(self, id : int):
        query = f'update addresses set is_visible = false where id = {id}'
        
        await self.db.execute(command=query, fetch=False)

    async def add(self,user_id :int = 0,index : str = '',country : str = '',
                  city : str = '',street : str = '',house : str = '',
                  building : str = '',office : str = '', is_visible=True):
        
        query = \
        f"insert into addresses (user_id, index, country, city, street, \
        house, building, office, is_visible, is_takeaway) values({user_id}, '{index}', '{country}', \
        '{city}', '{street}', '{house}', '{building}', '{office}', '{is_visible}', False)" 
        
        await self.db.execute(command=query, fetch=False)
           