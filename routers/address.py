from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from models.db_context import DBContext
from models.fsm import AddressState, PurchaseState
from models.callback_factory import AddressCallbackFactory
from routers.utils import AddressKeyboards, MenuKeyboards
from routers.purchase import AcceptanceForm

class AddressRouter:
    cities = ['Красноярск']

    router = Router()
        
#Menu message handler
###################################

@AddressRouter.router.message(F.text ==  'Мои адреса')
async def address_menu(message : Message, db_context : DBContext):
    
    #Check Address
    ads = await db_context.addresses.get_by_user_id(message.from_user.id)
    if ads == []:
        caption = 'Здесь пока ничего нет'
    else:
        caption = 'Ваши адреса:'

    #answer
    await message.answer_photo( photo=await db_context.images.get_by_name('PhotoArtComplect'),
        caption=caption,
        reply_markup=AddressKeyboards.list_addresses(ads))



#Remove callbak handler
###################################        

@AddressRouter.router.callback_query(AddressState.delete_address, AddressCallbackFactory.filter())
async def chosen_address_to_delete(call : CallbackQuery, callback_data : AddressCallbackFactory, state : FSMContext, db_context : DBContext):
    match callback_data.action:
        
        case 'address':
            address = (await db_context.addresses.get_by_user_id(call.from_user.id))[callback_data.address_index]
            await db_context.addresses.delete_by_id(address.id)

        case _:
            pass
    
    result_addresses = await db_context.addresses.get_by_user_id(call.from_user.id)

    await call.message.edit_caption(
        caption= 'Здесь пока ничего нет' if result_addresses == [] else 'Ваши адреса:',
        reply_markup=AddressKeyboards.list_addresses(result_addresses)
        )

    await state.clear()
    await call.answer()



#Menu callback handler
####################################

@AddressRouter.router.callback_query(AddressCallbackFactory.filter())
async def will_to_change_address(call : CallbackQuery, callback_data : AddressCallbackFactory , state : FSMContext, db_context : DBContext) :

    match callback_data.action:
        case 'address':
            if (await state.get_state()) == PurchaseState.ChooseAddress:
                await state.set_state(PurchaseState.Accept)
                await state.update_data(chosen_address = callback_data.address_id)
                await state.update_data(order=await AcceptanceForm(call=call, state=state, db_context=db_context)) 

        case 'remove':
            await state.set_state(AddressState.delete_address)
            await call.message.edit_caption(caption= 'Выберите адрес который хотите удалить',
                reply_markup=AddressKeyboards.list_addresses(await db_context.addresses.get_by_user_id(call.from_user.id), 
                remove=True))

        case 'add':
            await state.set_state(AddressState.choose_city)
            await call.message.answer('''Выберите город:''', reply_markup=AddressKeyboards.list_cities(AddressRouter.cities))
            #await call.message.edit_reply_markup(
            #    reply_markup=addresses_keyboard(await db_context.addresses.get_addresses_by_user_id(call.from_user.id)))
        case 'takeaway':
            ta_adresses = await db_context.addresses.get_takeaway_addresses()
            await call.message.edit_caption(
                caption='Выберите адрес для самовывоза', 
                reply_markup=AddressKeyboards.list_addresses_for_purchase(ta_adresses, is_takeaway=True))
        case 'delivery':
            await call.message.edit_caption(
                caption='Выберите адрес доставки', 
                reply_markup=AddressKeyboards.list_addresses_for_purchase(await db_context.addresses.get_by_user_id(call.message.chat.id)))
    await call.answer()



#Add city message handler
###################################

@AddressRouter.router.message(AddressState.choose_city, F.text.in_(AddressRouter.cities))
async def add_city(message : Message, db_context : DBContext, state : FSMContext):
    await state.update_data(city = message.text)
    await message.reply('Теперь укажите улицу', reply_markup=MenuKeyboards.show_cancel_button())
    await state.set_state(AddressState.choose_street)

@AddressRouter.router.message(AddressState.choose_street)
async def add_street(message : Message, db_context : DBContext, state : FSMContext):
    await state.update_data(street = message.text)
    await message.reply('Принято, теперь укажите номер дома', reply_markup=MenuKeyboards.show_cancel_button())
    await state.set_state(AddressState.choose_house)

@AddressRouter.router.message(AddressState.choose_house)
async def add_house(message : Message, db_context : DBContext, state : FSMContext):
    await state.update_data(house = message.text)
    await message.reply('Принято, теперь укажите строение', reply_markup=AddressKeyboards.show_cancel_button())
    await state.set_state(AddressState.choose_building)

@AddressRouter.router.message(AddressState.choose_building, F.text == 'Пропустить')
async def add_empty_building(message : Message, db_context : DBContext, state : FSMContext):
    await state.update_data(building = '')
    await message.reply('Принято, теперь укажите номер офиса или квартиры', reply_markup=AddressKeyboards.show_cancel_button())
    await state.set_state(AddressState.choose_office)

@AddressRouter.router.message(AddressState.choose_building)
async def add_building(message : Message, db_context : DBContext, state : FSMContext):
    await state.update_data(building = message.text)
    await message.reply('Принято, теперь укажите номер офиса или квартиры', reply_markup=AddressKeyboards.show_cancel_button())
    await state.set_state(AddressState.choose_office)

@AddressRouter.router.message(AddressState.choose_office,F.text == 'Пропустить')
async def add_empty_office(message : Message, db_context : DBContext, state : FSMContext):
    await state.update_data(office = '')
    await message.reply('Принято, теперь укажите индекс', reply_markup=MenuKeyboards.show_cancel_button())
    await state.set_state(AddressState.choose_index)

@AddressRouter.router.message(AddressState.choose_office)
async def add_office(message : Message, db_context : DBContext, state : FSMContext):
    await state.update_data(office = message.text)
    await message.reply('Принято, теперь укажите индекс', reply_markup=MenuKeyboards.show_cancel_button())
    await state.set_state(AddressState.choose_index)

@AddressRouter.router.message(AddressState.choose_index)
async def add_street(message : Message, db_context : DBContext, state : FSMContext):
    data = (await state.get_data())
    await db_context.addresses.add(
        user_id=message.from_user.id,
        index= message.text,
        country='РФ',
        city=data['city'],
        street=data['street'],
        house=data['house'],
        building=data['building'],
        office=data['office']
    )
    await message.answer('Заверешено', reply_markup=MenuKeyboards.get_menu())
    user_addresses = await db_context.addresses.get_by_user_id(message.from_user.id)
    if user_addresses == []:
        caption = 'Здесь пока ничего нет'
    else:
        caption = 'Ваши адреса:'

    #answer
    await message.answer_photo( photo=await db_context.images.get_by_name('PhotoArtComplect'),
        caption=caption,
        reply_markup=AddressKeyboards.list_addresses(user_addresses))

