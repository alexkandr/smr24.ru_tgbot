from aiogram import Router, html, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from models.db import images, items
from models.seo_texts import search_text
from models.fsm import SearchState
from models.keyboards import MenuKeyboards, CatalogKeyboards

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
    showing_data = await items.find(query= message.text)
    #Check for empty
    if showing_data == []:
        await message.answer(text=f'Ничего не найдено по запросу {message.text}')
        return

    #Show items
    for item in showing_data:
        await message.answer_photo(photo= item.image, caption=(item.message_info()),
        reply_markup= CatalogKeyboards.show_item(0, item.id))