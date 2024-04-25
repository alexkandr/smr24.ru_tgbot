from datetime import datetime
from decimal import *
from aiogram import html
from dataclasses import dataclass


@dataclass
class ItemDAO:
    id: str
    group_name : str
    name: str  
    description: str  
    manufacturer_name : str
    image : str  
    price_per_unit : Decimal
    units : str
    currency : str
    avaible : int = 0
    
    def __init__(self, id : str , group_name : str, name : str, description : str, manufacturer_name : str, image : str, price_per_unit : int, units : str, currency : str, avaible : int) -> None:
        self.id = id
        self.group_name = group_name
        self.name = name
        self.description = description
        self.manufacturer_name = manufacturer_name
        self.image = image
        self.price_per_unit = price_per_unit
        self.units = units
        self.currency = currency
        self.avaible = avaible
        
    def values_as_tuple(self) -> tuple[str, str, str, str, str, int, Decimal, str, str, int]:
        return (self.id, self.name, self.description, self.group_name, self.manufacturer_name, self.image, self.price_per_unit, self.units, self.currency, self.avaible)
    
    def price_str(self) -> str:
        return str(self.price_per_unit) + ' за ' + self.units

    def message_info(self) -> str:
        return (f"{self.name}\n"
            f"<b><i>Категория:</i></b> \n {self.group_name}\n" 
            f"<b><i>Описание:</i></b> \n {self.description}\n"
            f"<b><i>Производитель:</i></b> {self.manufacturer_name}\n"
            f"<b><i>Цена:</i></b> {self.price_str()}" 
            )
        
@dataclass
class CartItemDAO:
    user_id : int
    item_id : int
    amount : int
    def __int__(self, user_id : int, item_id : int, amount : int):
        self.amount = amount
        self.user_id = user_id
        self.item_id = item_id

    def values_as_tuple(self) -> tuple[int, int, int]:
        return (self.user_id, self.item_id, self.amount)
@dataclass
class OrderItemDAO:
    order_id : int
    item_id : int
    amount : int
    def __int__(self, order_id : int, item_id : int,  amount : int):
        self.amount = amount
        self.item_id = item_id
        self.order_id = order_id

    def values_as_tuple(self) -> tuple[int, int, int]:
        return (self.order_id, self.item_id, self.amount)

@dataclass
class OrderDAO:
    id : int
    user_id : int
    address_id : int
    total_sum : Decimal
    payment_method : str
    status : str
    creating_time : datetime

    def __init__(self, id : int = 0, user_id : int = 0, address_id : int = 0, total_sum : Decimal = 0, payment_method : str = '', status : str = 'created', creating_time : datetime = datetime.now()):
        self.id = id
        self.user_id = user_id
        self.address_id = address_id
        self.total_sum = total_sum
        self.payment_method = payment_method
        self.status = status
        self.creating_time = creating_time

    def values_as_tuple(self) -> tuple[int, int, Decimal, str, str, datetime]:
        return (self.user_id, self.address_id, self.total_sum, self.payment_method, self.status, self.creating_time)
    
@dataclass
class AddressDAO:
    id : int
    user_id :int
    index : str
    country : str
    city : str
    street : str
    house : str
    building : str
    office : str
    visible:bool

    def __init__(self, id : int = 0,user_id :int = 0,index : str = '',country : str = '',city : str = '',street : str = '',house : str = '',building : str = '',office : str = '', visible=True):
        self.id =  id 
        self.user_id=  user_id
        self.index =  index 
        self.country =  country 
        self.city =  city 
        self.street =  street 
        self.house =  house 
        self.building =  building 
        self.office =  office 
        self.visible= visible

    def values_as_tuple(self) ->tuple[int,int,str,str,str,str,str,str,str]:
        return (self.id, self.user_id, self.index, self.country, self.city, self.street, self.house, self.building, self.office)
    def to_string(self) ->str:
        return ', '.join([self.index, self.country , self.city , self.street , self.house , self.building , self.office])