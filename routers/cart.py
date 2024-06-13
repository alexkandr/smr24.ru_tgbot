from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from models.callback_factory import CartCallbackFactory
from models.keyboards import CartKeyboards, AddressKeyboards
from models.fsm import PurchaseState
from models.db import carts, images, addresses, items

router = Router()

cart_message = 'Чего-то не хватает? \n Жми -> /catalog'

@router.message(F.text == 'Корзина')
async def cart_menu(message : Message):
    
    cart = await carts.get_cart(message.from_user.id)

    if cart:
        await message.answer_photo(photo=await images.get_by_name('PhotoArtComplect'),
        caption=cart_message,
        reply_markup=await CartKeyboards.get_cart(cart, message.from_user.id))
        return 
    
    await message.answer_photo( photo=await images.get_by_name('PhotoArtComplect'), caption=cart_message)

    
@router.callback_query(CartCallbackFactory.filter())
async def cart_action(call : CallbackQuery, callback_data : CartCallbackFactory, state : FSMContext):
    match callback_data.action:
        case 'clear':
            await carts.clear_cart(callback_data.user_id)
            await call.message.edit_reply_markup(reply_markup=None)
            await call.answer(text='Корзина очищена', show_alert=True)
        case 'buy':
            await state.set_state(PurchaseState.ChooseAddress)
            await call.message.answer_photo(
                photo=await images.get_by_name('PhotoArtComplect'),
                caption='Выберите адрес доставки', 
                reply_markup=AddressKeyboards.list_addresses_for_purchase(await addresses.get_by_user_id(callback_data.user_id)))
            await call.answer()
        case 'info':
            item = await items.get_by_id(callback_data.item_id)
            await call.message.edit_caption(caption=item.message_info(),
                                            reply_markup=CartKeyboards.show_item(amount=callback_data.amount, item_id=callback_data.item_id, user_id=callback_data.user_id))
            await  call.answer()
        case 'save':
            new_cart = await carts.set_amount(user_id=callback_data.user_id, item_id=callback_data.item_id, amount=callback_data.amount)
            await call.message.edit_caption(caption=cart_message,
                reply_markup = (await CartKeyboards.get_cart(cart=new_cart, user_id=callback_data.user_id)))
            await  call.answer()
        case 'delete':
            new_cart = await carts.remove_item(user_id=callback_data.user_id, item_id=callback_data.item_id)
            await call.message.edit_caption(caption=cart_message,
                reply_markup = (await CartKeyboards.get_cart(cart=new_cart, user_id=callback_data.user_id)))
            await  call.answer()
        case 'decr':
            item = await items.get_by_id(callback_data.item_id)
            await call.message.edit_caption(caption = item.message_info(),
                                            reply_markup = CartKeyboards.show_item(amount=callback_data.amount - 1, item_id=callback_data.item_id, user_id=callback_data.user_id))
            await  call.answer()
        case 'incr':
            item = await items.get_by_id(callback_data.item_id)
            await call.message.edit_caption(caption = item.message_info(),
                                            reply_markup = CartKeyboards.show_item(amount=callback_data.amount + 1, item_id=callback_data.item_id, user_id=callback_data.user_id))
            await  call.answer()