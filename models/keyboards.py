from aiogram.types import ReplyKeyboardMarkup,InlineKeyboardMarkup, \
      KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
import decimal

from models.callback_factory import AddressCallbackFactory, \
      ItemCallbackFactory, CartCallbackFactory, CategoryCallbackFactory
from models.db import items
from models.dao import CartItemDAO, AddressDAO
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
    def list_payment_method() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text='Наличными при получении', callback_data='cash')
        builder.button(text='Переводом при получении', callback_data='transfer')
        builder.button(text='Отмена', callback_data='cancel')
        builder.adjust(1)
        return builder.as_markup()



class MenuKeyboards:

    @staticmethod 
    def get_menu() -> ReplyKeyboardMarkup:
        
        builder = ReplyKeyboardBuilder()    
        for name in ['Каталог', 'Поиск', 'Корзина', 'Адрес', 'Связь']:
            builder.add(KeyboardButton(text=name))
        builder.adjust(3)

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

    @staticmethod
    def list_categories(category_ids: list[str], page : int, category_dict : dict) -> InlineKeyboardMarkup:
        
        buttons = []
        
        for cat in category_ids:
            buttons.append([InlineKeyboardButton(text=category_dict[cat], callback_data=CategoryCallbackFactory(c=str(cat), manufacturer='').pack())])
        buttons.append([
                InlineKeyboardButton(text="<", callback_data=CategoryCallbackFactory(c='-' + str(page), manufacturer = '').pack()),
                InlineKeyboardButton(text=str(page), callback_data=CategoryCallbackFactory(c='curr', manufacturer = '').pack()),
                InlineKeyboardButton(text=">", callback_data=CategoryCallbackFactory(c='+' + str(page), manufacturer = '').pack())
            ])


        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def list_manufacturers(manufacturers: list[str], category : str) -> InlineKeyboardMarkup:
        
        buttons = []
        
        for man in manufacturers:
            buttons.append([InlineKeyboardButton(text=man, callback_data=CategoryCallbackFactory(c=category, manufacturer=man).pack()) ])
        buttons.append([
                #InlineKeyboardButton(text="Другое", callback_data=CategoryCallbackFactory(c=category, manufacturer='other').pack()),
                InlineKeyboardButton(text="Назад", callback_data=CategoryCallbackFactory(c='back', manufacturer = '').pack())
            ])


        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod 
    def show_item(amount : int, item_id : int) -> InlineKeyboardMarkup:
        
        builder = InlineKeyboardBuilder()
        
        builder.button(text="-1", callback_data=ItemCallbackFactory(action='decr', amount=amount, item_id=item_id))
        builder.button(text="+1", callback_data=ItemCallbackFactory(action='incr', amount=amount, item_id=item_id))
        
        builder.button(text=f'{amount} штук в корзину', callback_data=ItemCallbackFactory(action='to_cart', amount=amount, item_id=item_id))
        
        builder.adjust(2)

        return builder.as_markup(resize_keyboard=True)


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
                text=f'{item.name[:10]}... \n {line.amount}шт * {item.price_per_unit}руб = {t_price}руб', 
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
            text=f'Купить всё за {sum}руб', 
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



class PurchaseKeyboards:

    @staticmethod 
    def get_acceptance_form() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text='Подтверждаю заказ', callback_data='Accept')
        builder.button(text='Изменить заказ', callback_data='change')
        builder.adjust(1)
        return builder.as_markup()
    
class AdminKeyboards:
    @staticmethod
    def list_categories() -> InlineKeyboardMarkup:    
        builder = ReplyKeyboardBuilder()
        
        builder.button(text='chocolate')
        builder.button(text='sweet')
        builder.button(text='cake')
        builder.button(text='cookie')
        
        builder.adjust(1)

        return builder.as_markup()
