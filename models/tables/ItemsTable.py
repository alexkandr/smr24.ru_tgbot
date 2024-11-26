from psycopg.rows import class_row, dict_row
from models.dao import ItemDAO, OrderDAO, OrderItemDAO, CartItemDAO, AddressDAO, GroupDao
from models.db import DataBase

class ItemsTable:
    per_page = 7

    def __init__(self):
        self.db = DataBase()

    async def get_categories(self, page : int, parent : str = None) -> list[GroupDao]:
        if parent is None:
            query = f'''select * from groups where level = {2} offset {(page - 1)* self.per_page} limit {self.per_page}'''
            len_query = f'''select count(*) from groups where level = {2}'''
        else:
            query = f'''select * from groups where parent = '{parent}' offset {(page - 1)* self.per_page} limit {self.per_page}'''
            len_query = f'''select count(*) from groups where parent = '{parent}' '''
        result = await self.db.execute(command=query, factory=class_row(GroupDao),
                                  fetch=True)
        data_len = await self.db.execute(command=len_query, fetch=True)
        return result, int(data_len[0][0])
    
    async def get_category_by_id(self, id : int) -> GroupDao:
        query = f'''select * from groups where id = '{id}' '''
        result = await self.db.execute(command=query, factory=class_row(GroupDao),
                                  fetch=True)
        return result[0]

    def add_amount(self, id : int, amount : int) -> None:
        return
    
    def subtract_amount(self, id : int, amount : int) -> None:
        return
    
    async def get_all(self) -> list[ItemDAO]:
        query = f'select * from items'
        
        result = await self.db.execute(command=query, factory=class_row(ItemDAO),
                                  fetch=True)
        return result    
    
    async def get_manufacturers_by_category(self, category : str, available_only : bool = False) -> list[str]:
        if available_only:
            query = f"select distinct manufacturer_name from items where group_id = '{category}' and is_visible = True and available > 0 "
        else:
            query = f"select distinct manufacturer_name from items where group_id = '{category}' and is_visible = True"
        result = [r[0] for r in await self.db.execute(command=query,
                                  fetch=True)]
        return result, len(result)
    
    async def get_by_cat_man(self, category : str, manufacturer:str, page : int, available_only : bool = False) -> list[ItemDAO]:
        
        offset = (page-1)*self.per_page
        if manufacturer == 'other':
            query = f"select * from items where group_id = '{category}' and manufacturer_name is null and is_visible = True"
        else:
            if available_only:
                query = f"select * from items where group_id = '{category}' and manufacturer_name='{manufacturer}' and is_visible = True and available > 0 limit {self.per_page} offset {offset}"
                count_que = f"select count(*) from items where group_id = '{category}' and manufacturer_name='{manufacturer}' and is_visible = True and available > 0"
            else:
                query = f"select * from items where group_id = '{category}' and manufacturer_name='{manufacturer}' and is_visible = True limit {self.per_page} offset {offset}"
                count_que = f"select count(*) from items where group_id = '{category}' and manufacturer_name='{manufacturer}' and is_visible = True"
        
        result = await self.db.execute(command=query, factory=class_row(ItemDAO),
                                  fetch=True)
        count = await self.db.execute(command=count_que,
                                  fetch=True)        
        count = int(count[0][0])
        return result, count

    async def get_by_category(self, category : str) -> list[ItemDAO]:
        query = f"select * from items where group_id = '{category}' and is_visible = True"
        
        result = await self.db.execute(command=query, factory=class_row(ItemDAO),
                                  fetch=True)
        return result
    
    async def get_by_id(self, item_id : int) -> ItemDAO:
        query = f"select * from items where id = '{item_id}'"
        
        result = await self.db.execute(command=query, factory=class_row(ItemDAO),
                                  fetch=True)
        return result[0]
    
    async def get_names(self) -> list[dict]:
        return
    
    async def find(self, search : str, page : int, data_len : int=0) -> list[ItemDAO] | None:
        offset = (page -1)*self.per_page
        query = f"select * from items where to_tsvector(lower(name)) \
        @@ plainto_tsquery(lower('{search}')) and is_visible = True limit {self.per_page} offset {offset}"
        
        result = await self.db.execute(command=query, factory=class_row(ItemDAO),
                                  fetch=True)
        count_que  = f"select count(*) from items where to_tsvector(lower(name)) \
        @@ plainto_tsquery(lower('{search}')) and is_visible = True"
        count = data_len if data_len > 0 else int((await self.db.execute(command=count_que, fetch=True))[0][0])
        return result, count
