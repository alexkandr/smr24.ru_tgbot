from typing import Optional
from aiogram.filters.callback_data import CallbackData


class AddressCallbackFactory(CallbackData, prefix="address"):
    action : str
    address_index : Optional[int]
    address_id : Optional[int]


class CartCallbackFactory(CallbackData, prefix="cart"):
    action : str
    user_id : int
    item_id : Optional[str]
    amount : Optional[int]


class ItemCallbackFactory(CallbackData, prefix="item"):
    action : str
    item_id : str
    amount: int

class CategoryCallbackFactory(CallbackData, prefix="c"):
    c : str
    p : Optional[str]
    manufacturer: Optional[str]
    d : int

class ItemsListCallbackFactory(CallbackData, prefix="ilist"):
    action : str
    item_id : Optional[str]
    page : Optional[int]
    data_len : int
    c : str

class ItemsSearchCallbackFactory(CallbackData, prefix="slist"):
    action : str
    item_id : Optional[str]
    page : Optional[int]
    data_len : int

class OrderCallbackFactory(CallbackData, prefix="order"):
    action : str
    order_id : Optional[str]
    item_id : Optional[str]
    amount : Optional[int]