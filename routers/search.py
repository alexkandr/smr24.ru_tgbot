import math

from aiogram import Router, html, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from routers.utils import MenuKeyboards, CatalogKeyboards
from models.db_context import DBContext
from models.seo_texts import search_text
from models.fsm import SearchState
from models.callback_factory import ItemsSearchCallbackFactory


class SearchRouter():
    router = Router()

@SearchRouter.router.message(F.text == 'Поиск')
@SearchRouter.router.message(Command(commands=['Search']))
async def search_que(message : Message, db_context : DBContext, state : FSMContext):
    await message.answer_photo(
            photo=await db_context.images.get_by_name('PhotoArtComplect'),
            caption=search_text,
            reply_markup=MenuKeyboards.show_cancel_button())
    await state.set_state(SearchState.Search)

@SearchRouter.router.message(SearchState.Search)
async def search_results(message : Message, db_context : DBContext, state : FSMContext):
    showing_data, data_len = await db_context.items.find(search= message.text, page=1)
    #Check for empty
    if data_len == 0:
        await message.answer(text=f'Ничего не найдено по запросу {message.text}\nПопробуйте изменить запрос')
        return
    text = f'''Найдено {data_len} результатов
по запросу : {message.text}

⬇️       ⬇️       ⬇️       ⬇️       ⬇️       ⬇️'''
    await message.answer(text = text, reply_markup=CatalogKeyboards.list_search_items(showing_data, page=1, data_len=data_len))
         

@SearchRouter.router.callback_query(ItemsSearchCallbackFactory.filter())
async def list_items(call : CallbackQuery, callback_data : ItemsSearchCallbackFactory, db_context : DBContext):
    
    match(callback_data.action):
        case 'show':
            item = await db_context.items.get_by_id(callback_data.item_id)
            await call.message.answer_photo(photo= item.image, caption=(item.message_info()),reply_markup= CatalogKeyboards.show_item(0, item.id))
        case '>' :
            
            page = callback_data.page
            page = page + 1 if page*db_context.items.per_page < callback_data.data_len else 1
            rows = call.message.text.split('\n')
            search = rows[1][len('по запросу : ') :]
            showing_data, data_len = await db_context.items.find(search=search, page=page, data_len=callback_data.data_len)

            await call.message.edit_reply_markup(reply_markup=CatalogKeyboards.list_search_items(showing_data, page=page, data_len=data_len))
        case '<' :
            
            page = callback_data.page
            page = page -1 if page>1 else math.ceil(callback_data.data_len/ db_context.items.per_page)
            rows = call.message.text.split('\n')
            search = rows[1][len('по запросу : ') :]
            showing_data, data_len = await db_context.items.find(search=search, page=page, data_len=callback_data.data_len)
            
            await call.message.edit_reply_markup(reply_markup=CatalogKeyboards.list_search_items(showing_data, page=page, data_len=data_len))
        case 'delete' : 
            await call.message.delete()
        case _ : 
            pass
    
    await call.answer()