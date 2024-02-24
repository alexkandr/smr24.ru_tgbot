# coding=utf-8
from aiogram import Router, html, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from models.callback_factory import ItemCallbackFactory, CategoryCallbackFactory
from models.keyboards import CatalogKeyboards
from models.db import images_tab, items_tab, cart_tab
from models.seo_texts import search_text

router = Router()

@router.message(F.text=='Каталог')
@router.message(Command(commands=['catalog']))
async def catalog_que(message : Message):
    await message.answer_photo(photo=await images_tab.get_by_name('Catalog'),
        reply_markup=CatalogKeyboards.list_categories(await items_tab.get_categories(page = 1), page=1) )

@router.callback_query(CategoryCallbackFactory.filter())
async def show_catalog(call : CallbackQuery, callback_data : CategoryCallbackFactory):
    if callback_data.c.startswith('+'):
        nextpage = int(callback_data.c[1:]) + 1
        await call.message.edit_reply_markup(reply_markup=CatalogKeyboards.list_categories (await items_tab.get_categories(page = nextpage), page=nextpage))
        await call.answer()
        return
    if callback_data.c.startswith('-'):
        nextpage = int(callback_data.c[1:]) - 1
        await call.message.edit_reply_markup(reply_markup=CatalogKeyboards.list_categories (await items_tab.get_categories(page = nextpage), page=nextpage))
        await call.answer()
        return
    
    showing_data = await items_tab.get_by_category(callback_data.c)
    #Check for empty
    if showing_data == []:
        await call.message.answer(text='Здесь пока ничего нет')
        await call.answer()
        return

    #Show items
    for item in showing_data:
        await call.message.answer_photo(photo= item.image, caption=(item.message_info()),
        reply_markup= CatalogKeyboards.show_item(0, item.id))

    await call.answer()

async def update_item_markup(message: Message, new_amount : int, item_id : int):
    new_amount = new_amount if new_amount > 0 else 0
    await message.edit_reply_markup(reply_markup=CatalogKeyboards.show_item(new_amount, item_id))

@router.callback_query(ItemCallbackFactory.filter())
async def callback_catalog(call : CallbackQuery, callback_data : ItemCallbackFactory):
    
    match callback_data.action:
        case 'decr':
            await update_item_markup(call.message, callback_data.amount - 1, callback_data.item_id)
        case 'incr':
            await update_item_markup(call.message, callback_data.amount + 1, callback_data.item_id)
        case 'none':
            pass
        case 'to_cart':
            await update_item_markup(call.message, 0, callback_data.item_id)
            await cart_tab.add_to_cart(user_id=call.from_user.id, item_id=callback_data.item_id, amount= callback_data.amount)
            await call.answer(text=f'в корзину добавлено {callback_data.amount} штук', show_alert=True)
            return
    await call.answer()

