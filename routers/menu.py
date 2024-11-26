from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from routers.utils import MenuKeyboards
from models.db_context import DBContext
from models.seo_texts import start_command, contactus_command
from models.fsm import GiveIdState, GetNumber


class MenuRouter():
    ADMIN_CHAT_ID = ""
    router = Router()
    
    def __init__(self, admin_chat_id):    
        self.ADMIN_CHAT_ID = admin_chat_id

@MenuRouter.router.message(Command(commands=["start"]))
async def start(message : Message, db_context : DBContext, state : FSMContext):
    await state.set_state(GetNumber.Recieve_contact)
    m = await message.answer_photo(
        photo= await db_context.images.get_by_name('PhotoArtComplect'),
        caption=start_command, 
        reply_markup=MenuKeyboards.get_phone_number())
    
@MenuRouter.router.message(F.contact, GetNumber.Recieve_contact)
async def welcome(message: Message, state : FSMContext, db_context : DBContext):
    phnumber = message.contact.phone_number
    uid =  message.from_user.id
    await db_context.tusers.new_phone_number(phnumber, uid)

    await message.answer_photo(
        photo= await db_context.images.get_by_name('PhotoArtComplect'),
        caption='Добро пожаловать', 
        reply_markup=MenuKeyboards.get_menu())
    await state.clear()
    
@MenuRouter.router.message(GetNumber.Recieve_contact)
async def not_welcome(message: Message):
    await message.answer('Предоставьте, пожалуйста, номер телефона')

@MenuRouter.router.message(F.text == 'Связь')
async def contact_us_menu(message: Message, db_context : DBContext):
    
    await message.answer_photo(
        photo=await db_context.images.get_by_name('PhotoArtComplect'),
        caption= contactus_command,
        reply_markup=MenuKeyboards.get_contacts())

@MenuRouter.router.message(Command(commands=["cancel"]))
@MenuRouter.router.message(F.text.lower() == "отмена")
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Действие отменено",
        reply_markup=MenuKeyboards.get_menu()
    )

async def return_to_menu(message: Message, db_context : DBContext):
    await message.answer_photo(
        photo= await db_context.images.get_by_name('PhotoArtComplect'),
        caption=start_command, 
        reply_markup=MenuKeyboards.get_menu())

#save new image to db

@MenuRouter.router.message(Command(commands=['save_image']), F.chat.id.in_([MenuRouter.ADMIN_CHAT_ID]))
async def save_image(message : Message, db_context : DBContext, state : FSMContext):
    await state.set_state(GiveIdState.Recieve_image)
    await message.answer(text=f'Жду картинку, с подписью (названием файла)')


@MenuRouter.router.message(GiveIdState.Recieve_image, F.photo, F.chat.id.in_([MenuRouter.ADMIN_CHAT_ID]))
async def get_image_ig(message : Message, db_context : DBContext, state : FSMContext):
    await db_context.images.add(file_id=message.photo[0].file_id, file_name=message.caption)
    await state.clear()
    await message.answer(text=f'Сохранил')