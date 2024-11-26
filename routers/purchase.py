from decimal import Decimal

from aiogram import Router
from aiogram.types import  CallbackQuery
from aiogram.fsm.context import FSMContext

from routers.utils import PurchaseKeyboards
from models.fsm import PurchaseState
from models.dao import OrderDAO, CartItemDAO
from models.db_context import DBContext

class PurchaseRouter():
    router = Router()


@PurchaseRouter.router.callback_query(PurchaseState.Accept)
async def accept(call : CallbackQuery, state : FSMContext, db_context : DBContext):
    match call.data:
        case 'Accept':
            order = (await state.get_data())['order']
            order_id = await db_context.orders.add(order)
            cart = await db_context.carts.get_cart(call.from_user.id)
            for item in cart:
                await db_context.ordered_items.add_item(item_id=item.item_id, order_id=order_id, amount=item.amount)
            await db_context.carts.clear_cart(call.from_user.id)
            await state.clear()
            await call.message.answer(f'Ваш заказ сохранён под номером {order_id}.\n Ожидаем оплату')
        case _:
            await state.clear()
            #await call.message.answer(text='что теперб?')
    
    await call.answer()

async def AcceptanceForm(call : CallbackQuery, state: FSMContext, db_context : DBContext):
    data = await state.get_data()
    address = await db_context.addresses.get_by_id(data['chosen_address'])
    is_takeaway = await db_context.addresses.check_is_takeaway(address.id)
    curr_cart = await db_context.carts.get_cart(call.from_user.id)
    purchases, sum = await cart_to_str(curr_cart, db_context)
    await call.message.answer_photo(
        photo=await db_context.images.get_by_name('QRcode'),
        caption=f'''Давай всё проверим:
        Адрес {'самовывоза'if is_takeaway else'доставки'}: 
            {address.to_string()}
        Товары:{purchases}
        Всего:
            {sum} рублей
        Оплата:
            Поставщик: ООО "АртКомплект", ИНН 2465256841, КПП 246601001, 660048, Красноярский край, г.о. город Красноярск, г. Красноярск, ул Караульная, д. 7, тел.: 391241-85-44
            Получатель: ООО "АртКомплект"
            Банк получателя: КРАСНОЯРСКОЕ ОТДЕЛЕНИЕ N 8646 ПАО СБЕРБАНК г.Красноярск
            БИК: 040407627
            Номер счёта: 40702810231000007147
            ИНН: 2465256841
            КПП 246601001
            ''',
        reply_markup=PurchaseKeyboards.get_acceptance_form()
    )
    return OrderDAO(user_id=call.from_user.id, address_id=data['chosen_address'],
                      total_sum=sum, payment_method='bank_transfer', is_takeaway=is_takeaway)

async def cart_to_str(cart : list[CartItemDAO], db_context : DBContext):
    purchases = ''
    sum = Decimal(0)
    for line in cart:
        item = await db_context.items.get_by_id(line.item_id)
        purchases += f"\n{' '*12}{item.name} : \n {' '*20}{line.amount} штук по {item.price_per_unit}руб"
        sum += item.price_per_unit*int(line.amount)
    return (purchases, sum)


