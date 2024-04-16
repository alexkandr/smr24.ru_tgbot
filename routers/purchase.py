from aiogram import Router
from aiogram.methods import SendMessage
from aiogram.types import  CallbackQuery
from aiogram.fsm.context import FSMContext
from decimal import Decimal

from models.keyboards import PurchaseKeyboards
from models.fsm import PurchaseState
from models.dao import OrderDAO, CartItemDAO, OrderItemDAO
from models.db import cart_tab, orders_tab, ordered_items_tab, addresses_tab, items_tab


router = Router()


@router.callback_query(PurchaseState.Accept)
async def accept(call : CallbackQuery, state : FSMContext):
    match call.data:
        case 'Accept':
            order = (await state.get_data())['order']
            order_id = await orders_tab.add(order)
            cart = await cart_tab.get_cart(call.from_user.id)
            await ordered_items_tab.add_cart(cart, order_id)
            await cart_tab.clear_cart(call.from_user.id)
            await state.clear()
            await call.message.answer('Ваш заказ сохранён и скоро будет доставлен')
        case _:
            await state.clear()
            await call.message.answer(text='что теперб?')
    
    await call.answer()

async def AcceptanceForm(call : CallbackQuery, state: FSMContext):
    data = await state.get_data()
    address = await addresses_tab.get_by_id(data['chosen_address'])
    purchases = await cart_to_str(await cart_tab.get_cart(call.from_user.id))
    await call.message.answer(
        text=f'''Давай всё проверим:
        Адрес: 
            {address.to_string()}
        Товары:{purchases[0]}
        Всего:
            {purchases[1]} рублей
        Способ оплаты:
            По реквезитам $123456789$''',
        reply_markup=PurchaseKeyboards.get_acceptance_form()
    )
    return OrderDAO(user_id=call.from_user.id, address_id=data['chosen_address'], total_sum=purchases[1], payment_method='bank_transfer')

async def cart_to_str(cart : list[CartItemDAO]):
    purchases = ''
    sum = Decimal(0)
    for line in cart:
        item = await items_tab.get_by_id(line.item_id)
        purchases += f"\n{' '*12}{item.name} : \n {' '*20}{line.amount} штук по {item.price_per_unit}руб"
        sum += item.price_per_unit*int(line.amount)
    return (purchases, sum)


