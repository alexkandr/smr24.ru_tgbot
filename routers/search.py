from aiogram import Router, html, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from models.db import images, items
from models.seo_texts import search_text
from models.fsm import SearchState
from models.keyboards import MenuKeyboards, CatalogKeyboards
from models.callback_factory import ItemsSearchCallbackFactory
import math

router = Router()

@router.message(F.text == 'Поиск')
@router.message(Command(commands=['Search']))
async def search_que(message : Message, state : FSMContext):
    await message.answer_photo(
            photo=await images.get_by_name('PhotoArtComplect'),
            caption=search_text,
            reply_markup=MenuKeyboards.show_cancel_button())
    await state.set_state(SearchState.Search)

@router.message(SearchState.Search)
async def search_results(message : Message, state : FSMContext):
    showing_data, data_len = await items.find(search= message.text, page=1)
    #Check for empty
    if data_len == 0:
        await message.answer(text=f'Ничего не найдено по запросу {message.text}\nПопробуйте изменить запрос')
        return
    text = f'''Найдено {data_len} результатов
по запросу : {message.text}

⬇️       ⬇️       ⬇️       ⬇️       ⬇️       ⬇️'''
    await message.answer(text = text, reply_markup=CatalogKeyboards.list_search_items(showing_data, page=1, data_len=data_len))
         

@router.callback_query(ItemsSearchCallbackFactory.filter())
async def list_items(call : CallbackQuery, callback_data : ItemsSearchCallbackFactory):
    
    match(callback_data.action):
        case 'show':
            item = await items.get_by_id(callback_data.item_id)
            await call.message.answer_photo(photo= item.image, caption=(item.message_info()),reply_markup= CatalogKeyboards.show_item(0, item.id))
        case '>' :
            
            page = callback_data.page
            page = page + 1 if page*items.per_page < callback_data.data_len else 1
            rows = call.message.text.split('\n')
            search = rows[1][len('по запросу : ') :]
            showing_data, data_len = await items.find(search=search, page=page, data_len=callback_data.data_len)

            await call.message.edit_reply_markup(reply_markup=CatalogKeyboards.list_search_items(showing_data, page=page, data_len=data_len))
        case '<' :
            
            page = callback_data.page
            page = page -1 if page>1 else math.ceil(callback_data.data_len/ items.per_page)
            rows = call.message.text.split('\n')
            search = rows[1][len('по запросу : ') :]
            showing_data, data_len = await items.find(search=search, page=page, data_len=callback_data.data_len)
            
            await call.message.edit_reply_markup(reply_markup=CatalogKeyboards.list_search_items(showing_data, page=page, data_len=data_len))
        case 'delete' : 
            await call.message.delete()
        case _ : 
            pass
    
    await call.answer()