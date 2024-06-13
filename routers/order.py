import re
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from models.keyboards import OrdersKeyboards, CatalogKeyboards

from models.db import images, orders, items, ordered_items, addresses
from models.callback_factory import OrderCallbackFactory

router = Router()

@router.message(F.text ==  'Заказы')
async def list_orders(message : Message, user_id = 0):
    user_orders = await orders.get_by_user_id(message.from_user.id if user_id == 0 else user_id)
    caption = ''
    if user_orders == []:
        caption = 'Здесь пока ничего нет \n Жми -> /catalog'
    else:
        for order in user_orders:
            caption += order.short_info()
    await message.answer_photo(photo=await images.get_by_name('PhotoArtComplect'),
                               caption=caption)
    
@router.message(Command(re.compile(r'b_\d{18,20}')))
async def show_order(message : Message, command : CommandObject, state : FSMContext):
    order_id = command.regexp_match.string
    orderitems = await ordered_items.get_by_order_id(order_id)
    if orderitems == []:
        await message.answer('упс... кажется, ваш заказ пуст')
        return
    order = await orders.get_by_id(order_id)
    if order.user_id != message.from_user.id:
        await message.answer('упс... кажется, этот заказ пуст')
        return
    address = await addresses.get_by_id(order.address_id)
    await message.answer(text=order.long_info(address.to_string()), reply_markup=await \
                         OrdersKeyboards.get_order(orderitems, order))
    await state.update_data(order_id = order_id)
    
@router.callback_query(OrderCallbackFactory.filter())
async def chosen_address_to_delete(call : CallbackQuery, callback_data : OrderCallbackFactory, state : FSMContext):
    data = callback_data
    match data.action:
        case 'cancel':
            await orders.update_status(data.order_id, 'отменён', 'не требуется')
            await call.answer('Заказ отменён', show_alert=True)
            await list_orders(call.message, call.from_user.id)
        case 'restore':
            await orders.update_status(data.order_id, 'восстановлен', 'неоплачен')
            await call.answer('Заказ восстановлен', show_alert=True)
            await list_orders(call.message, call.from_user.id)
        case 'info':
            #todo: callbackfactory не вмещает одновременно order_id и item_id. 
            #поэтому при переходе на страницу товара нет возможности вернуться 
            #на тот же самый заказ
            item = await items.get_by_id(callback_data.item_id)
            await call.message.edit_text(text=item.message_info(),
                                            reply_markup=OrdersKeyboards.show_item(amount=callback_data.amount, order_id=callback_data.order_id, item_id=item.id))
            await  call.answer()
        case 'back':
            order_id = (await state.get_data())['order_id']
            order = (await orders.get_by_id(order_id))
            address = await addresses.get_by_id(order.address_id)
            orderitems = await ordered_items.get_by_order_id(order.id)
            await call.message.edit_text(text=order.long_info(address.to_string()),
                                            reply_markup= await OrdersKeyboards.get_order(orderitems, order))
        case 'sum':
            item = await items.get_by_id(callback_data.item_id)
            await call.message.answer_photo(photo= item.image, caption=(item.message_info()),reply_markup= CatalogKeyboards.show_item(0, item.id))
            await call.answer()


    
    