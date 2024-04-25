import random
from re import Match

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from models.db import addresses, images
from models.fsm import AddressState, PurchaseState
from models.callback_factory import AddressCallbackFactory
from models.keyboards import AddressKeyboards, MenuKeyboards
from routers.purchase import AcceptanceForm

router = Router()
cities = ['Красноярск']

#Menu message handler
###################################

@router.message(F.text ==  'Адрес')
async def address_menu(message : Message):
    
    #Check Address
    addresses = await addresses.get_by_user_id(message.from_user.id)
    if addresses == []:
        caption = 'Здесь пока ничего нет'
    else:
        caption = 'Ваши адреса:'

    #answer
    await message.answer_photo( photo=await images.get_by_name('PhotoArtComplect'),
        caption=caption,
        reply_markup=AddressKeyboards.list_addresses(addresses))



#Remove callbak handler
###################################        

@router.callback_query(AddressState.delete_address, AddressCallbackFactory.filter())
async def chosen_address_to_delete(call : CallbackQuery, callback_data : AddressCallbackFactory, state : FSMContext):
    match callback_data.action:
        
        case 'address':
            addresses = await addresses.get_by_user_id(call.from_user.id)
            address = addresses[callback_data.address_index]
            await addresses.delete_by_id(address.id)

        case _:
            pass
    
    result_addresses = await addresses.get_by_user_id(call.from_user.id)

    await call.message.edit_caption(
        caption= 'Здесь пока ничего нет' if result_addresses == [] else 'Ваши адреса:',
        reply_markup=AddressKeyboards.list_addresses(result_addresses)
        )

    await state.clear()
    await call.answer()



#Menu callback handler
####################################

@router.callback_query(AddressCallbackFactory.filter())
async def will_to_change_address(call : CallbackQuery, callback_data : AddressCallbackFactory , state : FSMContext) :

    match callback_data.action:
        case 'address':
            if (await state.get_state()) == PurchaseState.ChooseAddress:
                await state.set_state(PurchaseState.Accept)
                await state.update_data(chosen_address = callback_data.address_id)
                await state.update_data(order=await AcceptanceForm(call=call, state=state))
                await call.message.delete()  

        case 'remove':
            await state.set_state(AddressState.delete_address)
            await call.message.edit_caption(caption= 'Выберите адрес который хотите удалить',
                reply_markup=AddressKeyboards.list_addresses(await addresses.get_by_user_id(call.from_user.id), 
                remove=True))

        case 'add':
            await state.set_state(AddressState.choose_city)
            await call.message.answer('''Выберите город:''', reply_markup=AddressKeyboards.list_cities(cities))
            #await call.message.edit_reply_markup(
            #    reply_markup=addresses_keyboard(await addresses.get_addresses_by_user_id(call.from_user.id)))
    await call.answer()



#Add city message handler
###################################

@router.message(AddressState.choose_city, F.text.in_(cities))
async def add_city(message : Message, state : FSMContext):
    await state.update_data(city = message.text)
    await message.reply('Теперь укажите улицу', reply_markup=MenuKeyboards.show_cancel_button())
    await state.set_state(AddressState.choose_street)

@router.message(AddressState.choose_street)
async def add_street(message : Message, state : FSMContext):
    await state.update_data(street = message.text)
    await message.reply('Принято, теперь укажите номер дома', reply_markup=MenuKeyboards.show_cancel_button())
    await state.set_state(AddressState.choose_house)

@router.message(AddressState.choose_house)
async def add_house(message : Message, state : FSMContext):
    await state.update_data(house = message.text)
    await message.reply('Принято, теперь укажите строение', reply_markup=MenuKeyboards.show_cancel_button())
    await state.set_state(AddressState.choose_building)

@router.message(AddressState.choose_building)
async def add_building(message : Message, state : FSMContext):
    await state.update_data(building = message.text)
    await message.reply('Принято, теперь укажите номер офиса или квартиры', reply_markup=MenuKeyboards.show_cancel_button())
    await state.set_state(AddressState.choose_office)

@router.message(AddressState.choose_office)
async def add_office(message : Message, state : FSMContext):
    await state.update_data(office = message.text)
    await message.reply('Принято, теперь укажите индекс', reply_markup=MenuKeyboards.show_cancel_button())
    await state.set_state(AddressState.choose_index)

@router.message(AddressState.choose_index)
async def add_street(message : Message, state : FSMContext):
    data = (await state.get_data())
    await addresses.add(
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
    addresses = await addresses.get_by_user_id(message.from_user.id)
    if addresses == []:
        caption = 'Здесь пока ничего нет'
    else:
        caption = 'Ваши адреса:'

    #answer
    await message.answer_photo( photo=await images.get_by_name('PhotoArtComplect'),
        caption=caption,
        reply_markup=AddressKeyboards.list_addresses(addresses))

