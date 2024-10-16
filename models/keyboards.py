from aiogram.types import ReplyKeyboardMarkup,InlineKeyboardMarkup, \
      KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
import decimal
import math

from models.callback_factory import AddressCallbackFactory, \
      ItemCallbackFactory, CartCallbackFactory, CategoryCallbackFactory, OrderCallbackFactory,\
      ItemsListCallbackFactory, ItemsSearchCallbackFactory
from models.db import items
from models.dao import CartItemDAO, AddressDAO, OrderItemDAO, OrderDAO, ItemDAO, GroupDao
from models.seo_texts import contactus_url, contactus_text


class AddressKeyboards:

    @staticmethod
    def list_cities(cities : list[str]) -> ReplyKeyboardMarkup:
        builder = ReplyKeyboardBuilder()
        for o in cities:
            builder.button(text=o)
        builder.adjust(4)
        builder.button(text='отмена')
        return builder.as_markup(resize_keyboard=True)

    @staticmethod
    def list_addresses(addresses : list[AddressDAO], 
                       remove : bool = False) -> InlineKeyboardMarkup:

        builder = InlineKeyboardBuilder()
        for i, address in enumerate(addresses):
            builder.button(text= address.to_string(), callback_data=
                           AddressCallbackFactory(action='address', 
                                                    address_index=i, 
                                                    address_id=address.id))   
        
        if remove == True:
            builder.button(text='Отмена', callback_data=
                           AddressCallbackFactory(action='cancel', 
                                                    address_index=None, 
                                                    address_id=None))
            builder.adjust(1)
            return builder.as_markup()
        builder.button(text='Добавить', callback_data=
                       AddressCallbackFactory(action='add', 
                                                address_index=None, 
                                                address_id=None))
        if addresses != []:
            builder.button(text='Удалить', callback_data=
                           AddressCallbackFactory(action='remove',
                                                    address_index=None, 
                                                    address_id=None))
        builder.adjust(1)

        return builder.as_markup(resize_keyboard=False)
    
    @staticmethod
    def list_addresses_for_purchase(addresses : list[AddressDAO], 
                       remove : bool = False, is_takeaway : bool = False) -> InlineKeyboardMarkup:

        builder = InlineKeyboardBuilder()
        if not is_takeaway:
            builder.button(text='Самовывоз', callback_data=
                           AddressCallbackFactory(action='takeaway', 
                                                    address_index=None, 
                                                    address_id=None))
        
        for i, address in enumerate(addresses):
            builder.button(text= address.to_string(), callback_data=
                           AddressCallbackFactory(action='address', 
                                                    address_index=i, 
                                                    address_id=address.id))   
        
        if remove == True:
            builder.button(text='Отмена', callback_data=
                           AddressCallbackFactory(action='cancel', 
                                                    address_index=None, 
                                                    address_id=None))
            builder.adjust(1)
            return builder.as_markup()
        if not is_takeaway:
            builder.button(text='Добавить адрес доставки', callback_data=
                           AddressCallbackFactory(action='add', 
                                                    address_index=None, 
                                                    address_id=None))
            if addresses != []:
                builder.button(text='Удалить адреc доставки', callback_data=
                               AddressCallbackFactory(action='remove',
                                                        address_index=None, 
                                                        address_id=None))
        else: 
             builder.button(text='Доставка', callback_data=
                           AddressCallbackFactory(action='delivery', 
                                                    address_index=None, 
                                                    address_id=None))
        builder.adjust(1)

        return builder.as_markup(resize_keyboard=False)

    @staticmethod
    def list_payment_method() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text='Наличными при получении', callback_data='cash')
        builder.button(text='Переводом при получении', callback_data='transfer')
        builder.button(text='Отмена', callback_data='cancel')
        builder.adjust(1)
        return builder.as_markup()
    
    @staticmethod
    def show_cancel_button() -> ReplyKeyboardMarkup:
        builder = ReplyKeyboardBuilder()
        builder.button(text='Пропустить')
        builder.button(text='отмена')
        builder.adjust(1)
        return builder.as_markup()


class MenuKeyboards:
    @staticmethod
    def get_phone_number() -> ReplyKeyboardMarkup:
        builder = ReplyKeyboardBuilder()
        builder.button(text='Предоставить номер телефона', request_contact = True)
        return builder.as_markup()

    @staticmethod 
    def get_menu() -> ReplyKeyboardMarkup:
        
        builder = ReplyKeyboardBuilder()    
        for name in ['Каталог', 'Поиск', 'Корзина', 'Заказы', 'Мои адреса', 'Связь']:
            builder.add(KeyboardButton(text=name))
        builder.adjust(2)

        return builder.as_markup(resize_keyboard=True)

    @staticmethod 
    def get_contacts() -> InlineKeyboardMarkup:

        builder = InlineKeyboardBuilder()
        builder.button(text=contactus_text, url=contactus_url)

        builder.adjust(2)

        return builder.as_markup(resize_keyboard=True)

    @staticmethod
    def show_cancel_button() -> ReplyKeyboardMarkup:
        builder = ReplyKeyboardBuilder()
        builder.button(text='отмена')
        return builder.as_markup(resize_keyboard=True)


class CatalogKeyboards:

    
    ##@staticmethod
    ##def list_categories(category_ids: list[str], page : int, category_dict : dict) -> InlineKeyboardMarkup:
    ##    
    ##    buttons = []
    ##    
    ##    for cat in category_ids:
    ##        buttons.append([InlineKeyboardButton(text=category_dict[cat], callback_data=CategoryCallbackFactory(c=str(cat), manufacturer='').pack())])
    ##    buttons.append([
    ##            InlineKeyboardButton(text="<", callback_data=CategoryCallbackFactory(c='-' + str(page), manufacturer = '').pack()),
    ##            InlineKeyboardButton(text=str(page), callback_data=CategoryCallbackFactory(c='curr', manufacturer = '').pack()),
    ##            InlineKeyboardButton(text=">", callback_data=CategoryCallbackFactory(c='+' + str(page), manufacturer = '').pack())
    ##        ])
    ##
    ##
    ##    return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    
    @staticmethod
    def list_categories(categories: list[GroupDao], page : int, data_len : int) -> InlineKeyboardMarkup:
        
        buttons = []
        parent = categories[0].parent
        for cat in categories:
            buttons.append([InlineKeyboardButton(text=cat.name, callback_data=CategoryCallbackFactory(c=cat.id, p = parent, manufacturer='', d = str(0)).pack())])
        if data_len > 7:
            buttons.append([
                InlineKeyboardButton(text="<", callback_data=CategoryCallbackFactory(c='-' + str(page), p = parent, manufacturer = '', d = str(data_len)).pack()),
                InlineKeyboardButton(text=str(page), callback_data=CategoryCallbackFactory(c='curr', p = parent, manufacturer = '', d = str(data_len)).pack()),
                InlineKeyboardButton(text=">", callback_data=CategoryCallbackFactory(c='+' + str(page),p = parent, manufacturer = '', d = str(data_len)).pack())
            ])
        if categories[0].level > 2:
            buttons.append([InlineKeyboardButton(text='Назад', callback_data=CategoryCallbackFactory(c='prev', p = parent, manufacturer = '', d = str(0)).pack()),])


        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def list_manufacturers(manufacturers: list[str], category : GroupDao, data_len : int) -> InlineKeyboardMarkup:
        
        buttons = []
        
        for man in manufacturers:
            buttons.append([InlineKeyboardButton(text=man, callback_data=CategoryCallbackFactory(c=category.id, p = category.parent, manufacturer=man, d = str(data_len)).pack()) ])
        if manufacturers == []:
            buttons.append([InlineKeyboardButton(text='Товары отсутствуют', callback_data=CategoryCallbackFactory(c='None', p = category.parent, manufacturer='', d = str(data_len)).pack()) ])
        buttons.append([
                InlineKeyboardButton(text="Назад", callback_data=CategoryCallbackFactory(c='back', p = category.parent, manufacturer = '', d = str(0)).pack())
            ])


        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def list_items(ilist : list[ItemDAO], page : int, data_len : int, category :str ) -> InlineKeyboardMarkup: 
        per_page = 7
        buttons = []
        for i in ilist:
            buttons.append([InlineKeyboardButton(text=i.name, callback_data= ItemsListCallbackFactory(action='show', item_id= i.id, page=page, data_len = data_len, c=category).pack())])
        if ilist == []:
            buttons.append([InlineKeyboardButton(text='Товары отсутствуют', callback_data= ItemsListCallbackFactory(action='none', item_id= '', page=page, data_len = data_len, c=category).pack())])
        if data_len > per_page:
            total_pages = math.ceil(data_len/ per_page)
            buttons.append(
            [
                InlineKeyboardButton(text="<", callback_data=ItemsListCallbackFactory(action='<', page=page, item_id='',data_len = data_len, c=category).pack()),
                InlineKeyboardButton(text=f'{page}/{total_pages}', callback_data=ItemsListCallbackFactory(action='curr', page=page, item_id='',data_len = data_len, c=category).pack()),
                InlineKeyboardButton(text=">", callback_data=ItemsListCallbackFactory(action='>', page=page, item_id='',data_len = data_len, c=category).pack())
            ]
            )
        buttons.append([InlineKeyboardButton(text='❌ Убрать', callback_data= ItemsListCallbackFactory(action='delete', item_id='', page=page,data_len = data_len, c=category).pack())])

        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def list_search_items(ilist : list[ItemDAO], page : int, data_len : int) -> InlineKeyboardMarkup: 
        per_page = 7
        buttons = []
        for i in ilist:
            buttons.append([InlineKeyboardButton(text=i.name, callback_data= ItemsSearchCallbackFactory(action='show', item_id= i.id, page=page, data_len=data_len).pack())])

        if data_len > per_page:
            total_pages = math.ceil(data_len/ per_page)
            buttons.append(
            [
                InlineKeyboardButton(text="<", callback_data=ItemsSearchCallbackFactory(action='<', page=page, item_id='',data_len=data_len).pack()),
                InlineKeyboardButton(text=f'{page}/{total_pages}', callback_data=ItemsSearchCallbackFactory(action='curr', page=page, item_id='',data_len=data_len).pack()),
                InlineKeyboardButton(text=">", callback_data=ItemsSearchCallbackFactory(action='>', page=page, item_id='',data_len=data_len).pack())
            ]
            )
        buttons.append([InlineKeyboardButton(text='❌ Убрать', callback_data= ItemsSearchCallbackFactory(action='delete', item_id='', page=page,data_len=data_len).pack())])

        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod 
    def show_item(amount : int, item_id : int, show_annotation: bool = True) -> InlineKeyboardMarkup:
        
        buttons = []
        
        buttons.append([InlineKeyboardButton(text="-1", callback_data=ItemCallbackFactory(action='decr', amount=amount, item_id=item_id).pack()),
        InlineKeyboardButton(text="+1", callback_data=ItemCallbackFactory(action='incr', amount=amount, item_id=item_id).pack())])
        
        buttons.append([InlineKeyboardButton(text=f'{amount} штук в корзину', callback_data=ItemCallbackFactory(action='to_cart', amount=amount, item_id=item_id).pack())])
        if show_annotation:
            buttons.append([InlineKeyboardButton(text='Аннотация', callback_data= ItemCallbackFactory(action='show_annotation', amount=amount, item_id=item_id).pack())])
        buttons.append([InlineKeyboardButton(text='❌ Убрать', callback_data= ItemCallbackFactory(action='delete', amount=amount, item_id=item_id).pack())])

        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def delete_button() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text='❌ Убрать', callback_data="delete_annotation")
        return builder.as_markup()

class CartKeyboards:

    @staticmethod 
    async def get_cart(cart : list[CartItemDAO], 
                       user_id : int) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        if cart is None:
            return builder.as_markup()

        sum = decimal.Decimal(0)
        for line in cart:
            item = await items.get_by_id(line.item_id)
            t_price = item.price_per_unit * line.amount
            builder.button(
                text=f'{item.name[:10]}... \n {line.amount}шт * {item.price_per_unit}₽/шт = {t_price}₽', 
                callback_data = 
                    CartCallbackFactory(action='info', user_id=user_id,
                                        item_id=item.id, amount=line.amount)
            )
            sum += t_price
        
        builder.button(
            text='Очистить Корзину', 
            callback_data=CartCallbackFactory(action='clear', user_id=user_id, 
                                              item_id=None, amount=None)
        )
        builder.button(
            text=f'Купить всё за {sum}₽', 
            callback_data=CartCallbackFactory(action='buy', user_id=user_id, 
                                              item_id=None, amount=None)
        )

        builder.adjust(1)

        return builder.as_markup()


    @staticmethod 
    def show_item(amount : int, item_id : str, 
                  user_id : int) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        
        builder.button(
            text="-1", 
            callback_data=CartCallbackFactory(action='decr', user_id=user_id, 
                                              amount=amount, item_id=item_id)
        )
        builder.button(
            text=str(amount), 
            callback_data=CartCallbackFactory(action='none', user_id=user_id,
                                              amount=amount, item_id=item_id)
        )
        builder.button(
            text="+1", 
            callback_data=CartCallbackFactory(action='incr', user_id=user_id,
                                              amount=amount, item_id=item_id)
        )
        builder.button(
            text='Удалить из корзины', 
            callback_data=CartCallbackFactory(action='delete', user_id=user_id,
                                              amount=amount, item_id=item_id)
        )
        builder.adjust(3)
        builder.button(
            text='Сохранить', 
            callback_data=CartCallbackFactory(action='save', user_id=user_id,
                                              amount=amount, item_id=item_id)
        )

        return builder.as_markup(resize_keyboard=True)

class OrdersKeyboards:
    @staticmethod 
    async def get_order(order_items : list[OrderItemDAO], order : OrderDAO,
                       ) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        sum = decimal.Decimal(0)
        for line in order_items:
            item = await items.get_by_id(line.item_id)
            t_price = item.price_per_unit * line.amount
            builder.button(
                text=f'{item.name[:10]}... \n {line.amount}шт * {item.price_per_unit}₽/шт = {t_price}₽', 
                callback_data = 
                    OrderCallbackFactory(action='info', order_id=None,
                                        item_id=item.id, amount=line.amount)
            )
            sum += t_price
        
        builder.button(
            text=f'Итоговая сумма {sum}руб', 
            callback_data=OrderCallbackFactory(action='sum', order_id=order.id, 
                                              item_id=None, amount=None)
        )

        if order.payment_status == 'неоплачен':
            builder.button(
            text=f'Отменить заказ', 
            callback_data=OrderCallbackFactory(action='cancel', order_id=order.id, 
                                              item_id=None, amount=None)
        )

        if order.status == 'отменён':
            builder.button(
            text=f'Восстановить заказ', 
            callback_data=OrderCallbackFactory(action='restore', order_id=order.id, 
                                              item_id=None, amount=None)
        )   

        builder.adjust(1)

        return builder.as_markup()
    
    @staticmethod 
    def show_item(amount : int,
                  order_id : str = None, item_id : str = None) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(
            text=f"В заказ добавлено {amount} штук", 
            callback_data=OrderCallbackFactory(action='sum', order_id=None,
                                              amount=None, item_id=item_id)
        )
    
        builder.button(
            text='Вернуться к заказу', 
            callback_data=OrderCallbackFactory(action='back', order_id=order_id,
                                              amount=amount, item_id=None)
        )
        builder.adjust(1)

        return builder.as_markup(resize_keyboard=True)

class PurchaseKeyboards:

    @staticmethod 
    def get_acceptance_form() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text='Подтверждаю заказ', callback_data='Accept')
        builder.button(text='Изменить заказ', callback_data='change')
        builder.adjust(1)
        return builder.as_markup()