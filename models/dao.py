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
    visible : bool = True
    avaible : int = 0
    
    def __init__(self, id : str , group_name : str, name : str, 
                 description : str, manufacturer_name : str, image : str, 
                 price_per_unit : int, units : str, currency : str, 
                 avaible : int, visible :bool = True) -> None:
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
        self.visible = visible
        
    def values_as_tuple(self) -> tuple[str, str, str, str, str, 
                                        int, Decimal, str, str, int, bool]:
        return (self.id, self.name, self.description, self.group_name, 
                self.manufacturer_name, self.image, self.price_per_unit, 
                self.units, self.currency, self.avaible, self.visible)
    
    def price_str(self) -> str:
        return str(self.price_per_unit) + ' за ' + self.units

    def message_info(self) -> str:
        return (f"{self.name}\n"
            f"<b><i>Категория:</i></b> \n {self.group_name}\n" 
            f"<b><i>Описание:</i></b> \n {self.description}\n"
            f"<b><i>Производитель:</i></b> {self.manufacturer_name}\n"
            f"<b><i>Цена:</i></b> {self.price_str()}\n" 
            f"<b><i>В наличии:</i></b> {self.avaible}"
            )
        
@dataclass
class CartItemDAO:
    user_id : int
    item_id : int
    amount : float
    def __int__(self, user_id : int, item_id : int, amount : int):
        self.amount = amount
        self.user_id = user_id
        self.item_id = item_id

    def values_as_tuple(self) -> tuple[int, int, int]:
        return (self.user_id, self.item_id, self.amount)
@dataclass
class OrderItemDAO:
    order_id : str
    item_id : int
    amount : int
    def __int__(self, order_id : str, item_id : int,  amount : int):
        self.amount = amount
        self.item_id = item_id
        self.order_id = order_id

    def values_as_tuple(self) -> tuple[int, int, int]:
        return (self.order_id, self.item_id, self.amount)

@dataclass
class OrderDAO:
    id : str
    user_id : int
    address_id : int
    total_sum : Decimal
    payment_method : str
    status : str
    payment_status :str
    creating_time : datetime
    is_takeaway : bool

    def __init__(self, id : str = '', user_id : int = 0, address_id : int = 0, 
                 total_sum : Decimal = 0, payment_method : str = '', 
                 status : str = 'создан', payment_status = 'неоплачен', creating_time : datetime = 
                 datetime.now(), is_takeaway : bool = False):
        self.id = id
        self.user_id = user_id
        self.address_id = address_id
        self.total_sum = total_sum
        self.payment_method = payment_method
        self.status = status
        self.payment_status = payment_status
        self.creating_time = creating_time
        self.is_takeaway = is_takeaway

    def values_as_tuple(self) -> tuple[int, int, Decimal, str, str, str, datetime]:
        return (self.user_id, self.address_id, self.total_sum, 
                self.payment_method, self.status, self.payment_status, self.creating_time, self.is_takeaway)
    
    def short_info(self) -> str:
        return f'''
Заказ номер /{self.id}:
    Дата : {self.creating_time.date()}
    Сумма : {self.total_sum} рублей
    Статус заказа: {self.status}
    Статус оплаты: {self.payment_status}'''

    def long_info(self, address: str ='') -> str:
        if self.payment_status == 'неоплачен':
            req = '''
Реквезиты для оплаты:
    Поставщик: ООО "АртКомплект", ИНН 2465256841, КПП 246601001, 660048, Красноярский край, г.о. город Красноярск, г. Красноярск, ул Караульная, д. 7, тел.: 391241-85-44
    Получатель: ООО "АртКомплект"
    Банк получателя: КРАСНОЯРСКОЕ ОТДЕЛЕНИЕ N 8646 ПАО СБЕРБАНК г.Красноярск
    БИК: 040407627
    Номер счёта: 40702810231000007147
    ИНН: 2465256841
    КПП 246601001
'''
        else:
            req = ''
        return f'''
Информация о заказе
Номер : /{self.id}
Дата : {self.creating_time.date()}
Сумма : {self.total_sum} рублей
Статус заказа: {self.status}
Способ оплаты: Банковский перевод
Статус оплаты: {self.payment_status}
Способ доставки: {'Самовывоз' if self.is_takeaway else 'Доставка'}
Адрес: {address}
''' + req + 'Состав заказа:'
    
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
        return (self.id, self.user_id, self.index, self.country, self.city, 
                self.street, self.house, self.building, self.office)
    def to_string(self) ->str:
        res = ', '.join([self.index, self.city , self.street , 
                          self.house])
        res += '/' + self.building if self.building != '' else ''
        res += ', кв. ' + self.office if self.office != '' else ''
        return res
