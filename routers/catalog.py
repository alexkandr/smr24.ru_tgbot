# coding=utf-8
import math
from aiogram import Router, html, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from models.callback_factory import ItemCallbackFactory, CategoryCallbackFactory, ItemsListCallbackFactory
from models.keyboards import CatalogKeyboards
from models.db import images, items, carts
from models.seo_texts import search_text

router = Router()

@router.message(F.text=='Каталог')
@router.message(Command(commands=['catalog']))
async def catalog_que(message : Message):
    categories, data_len = await items.get_categories(1)
    await message.answer_photo(photo=await images.get_by_name('PhotoArtComplect'),
        reply_markup=CatalogKeyboards.list_categories(categories, page=1, data_len=data_len) )

@router.callback_query(CategoryCallbackFactory.filter())
async def show_catalog(call : CallbackQuery, callback_data : CategoryCallbackFactory):
    if callback_data.manufacturer is not None:
        category = await items.get_category_by_id(callback_data.c)    
        showing_data, data_len = await items.get_by_cat_man(category.id, callback_data.manufacturer, page=1)
        #Show items
        text = f'''Категория : {category.name}
Производитель : {callback_data.manufacturer}

⬇️       ⬇️       ⬇️       ⬇️       ⬇️       ⬇️'''
        await call.message.answer(text = text
                                  , reply_markup=CatalogKeyboards.list_items(showing_data, page=1, data_len=data_len, category=category.id))
         
        await call.answer()
        return
    
    if callback_data.c.startswith('+'):
        nextpage = int(callback_data.c[1:]) + 1
        nextpage = 1 if nextpage > math.ceil( callback_data.d / 7)  else nextpage
        categories, data_len = await items.get_categories(page = nextpage, parent=callback_data.p)
        await call.message.edit_reply_markup(reply_markup=CatalogKeyboards.list_categories (categories, page=nextpage, data_len=data_len))
        await call.answer()
        return
    if callback_data.c.startswith('-'):
        nextpage = int(callback_data.c[1:]) - 1
        nextpage = math.ceil( callback_data.d / 7) if nextpage < 1   else nextpage
        categories, data_len = await items.get_categories(page = nextpage, parent=callback_data.p)
        await call.message.edit_reply_markup(reply_markup=CatalogKeyboards.list_categories (categories, page=nextpage, data_len=data_len))
        await call.answer()
        return
    
    if callback_data.c.startswith('prev'):
        pparent = await items.get_category_by_id(callback_data.p)
        categories, data_len = await items.get_categories(page = 1, parent=pparent.parent)
        await call.message.edit_reply_markup(reply_markup=CatalogKeyboards.list_categories(categories, page=1, data_len=data_len))
        await call.answer()
        return
    if callback_data.c.startswith('back'):
        categories, data_len = await items.get_categories(page = 1, parent=callback_data.p)
        await call.message.edit_reply_markup(reply_markup=CatalogKeyboards.list_categories(categories, page=1, data_len=data_len))
        await call.answer()
        return
    if callback_data.c.startswith('None'):
        await call.answer()
    
    subgroups, data_len = await items.get_categories(page= 1, parent=callback_data.c)
    if subgroups == []:
        category = await items.get_category_by_id(callback_data.c)
        manufacturers, data_len = await items.get_manufacturers_by_category(category=callback_data.c)
        await call.message.edit_reply_markup(reply_markup=CatalogKeyboards.list_manufacturers(manufacturers=manufacturers, category=category, data_len=data_len))
        await call.answer()
    else:
        await call.message.edit_reply_markup(reply_markup=CatalogKeyboards.list_categories(subgroups, page=1, data_len=data_len))


async def update_item_markup(message: Message, new_amount : int, item_id : int):
    new_amount = new_amount if new_amount > 0 else 0
    await message.edit_reply_markup(reply_markup=CatalogKeyboards.show_item(new_amount, item_id))

@router.callback_query(ItemsListCallbackFactory.filter())
async def list_items(call : CallbackQuery, callback_data : ItemsListCallbackFactory):
    
    match(callback_data.action):
        case 'show':
            item = await items.get_by_id(callback_data.item_id)
            await call.message.answer_photo(photo= item.image, caption=(item.message_info()),reply_markup= CatalogKeyboards.show_item(0, item.id))
        case '>' :
            
            page = callback_data.page
            page = page + 1 if page*items.per_page < callback_data.data_len else 1
            rows = call.message.text.split('\n')
            category = callback_data.c
            manufacturer = rows[1][len('Производитель : ') : ]
            
            
            showing_data, data_len = await items.get_by_cat_man(category, manufacturer, page=page)
            await call.message.edit_reply_markup(reply_markup=CatalogKeyboards.list_items(showing_data, page=page, data_len=data_len, category=category))
        case '<' :
            
            page = callback_data.page
            page = page -1 if page>1 else math.ceil(callback_data.data_len/ items.per_page)
            rows = call.message.text.split('\n')
            category = callback_data.c
            manufacturer = rows[1][len('Производитель : ') : ]

            showing_data, data_len = await items.get_by_cat_man(category, manufacturer, page=page)
            
            await call.message.edit_reply_markup(reply_markup=CatalogKeyboards.list_items(showing_data, page=page, data_len=data_len, category=category))
        case 'delete' : 
            await call.message.delete()
        case _ : 
            pass
    
    await call.answer()

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
            await carts.add_to_cart(user_id=call.from_user.id, item_id=callback_data.item_id, amount= callback_data.amount)
            await call.answer(text=f'в корзину добавлено {callback_data.amount} штук', show_alert=True)
            return
        case 'show_annotation':
            item = await items.get_by_id(callback_data.item_id)
            if item.has_annotation:
                await call.message.answer_document(item.annotation, reply_markup=CatalogKeyboards.delete_button())
            else:
                await call.answer(text=f'у данного товара нет инструкции', show_alert=True)
        case 'delete':
            await call.message.delete()
    await call.answer()

@router.callback_query(F.data == 'delete_annotation')
async def delete_annotation(call : CallbackQuery):
    await call.message.delete()
    await call.answer()

