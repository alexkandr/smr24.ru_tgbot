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
    manufacturer: Optional[str]