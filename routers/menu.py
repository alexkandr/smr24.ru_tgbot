from os import getenv
from dotenv import load_dotenv
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from models.keyboards import MenuKeyboards
from models.db import images, tusers
from models.seo_texts import start_command, contactus_command
from models.fsm import GiveIdState, GetNumber

load_dotenv()
ADMIN_CHAT_ID = int(getenv('ADMIN_CHAT_ID'))

router = Router()

@router.message(Command(commands=["start"]))
async def start(message : Message, state : FSMContext):
    await state.set_state(GetNumber.Recieve_contact)
    m = await message.answer_photo(
        photo= await images.get_by_name('PhotoArtComplect'),
        caption=start_command, 
        reply_markup=MenuKeyboards.get_phone_number())
    
@router.message(F.contact, GetNumber.Recieve_contact)
async def welcome(message: Message, state : FSMContext):
    phnumber = message.contact.phone_number
    uid =  message.from_user.id
    await tusers.new_phone_number(phnumber, uid)

    await message.answer_photo(
        photo= await images.get_by_name('PhotoArtComplect'),
        caption='Добро пожаловать', 
        reply_markup=MenuKeyboards.get_menu())
    await state.clear()
    
@router.message(GetNumber.Recieve_contact)
async def not_welcome(message: Message):
    await message.answer('Предоставьте, пожалуйста, номер телефона')

@router.message(F.text == 'Связь')
async def contact_us_menu(message: Message):
    
    await message.answer_photo(
        photo=await images.get_by_name('PhotoArtComplect'),
        caption= contactus_command,
        reply_markup=MenuKeyboards.get_contacts())

@router.message(Command(commands=["cancel"]))
@router.message(F.text.lower() == "отмена")
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Действие отменено",
        reply_markup=MenuKeyboards.get_menu()
    )

async def return_to_menu(message: Message):
    await message.answer_photo(
        photo= await images.get_by_name('PhotoArtComplect'),
        caption=start_command, 
        reply_markup=MenuKeyboards.get_menu())

#save new image to db

@router.message(Command(commands=['save_image']), F.chat.id.in_([ADMIN_CHAT_ID]))
async def save_image(message : Message, state : FSMContext):
    await state.set_state(GiveIdState.Recieve_image)
    await message.answer(text=f'Жду картинку, с подписью (названием файла)')


@router.message(GiveIdState.Recieve_image, F.photo, F.chat.id.in_([ADMIN_CHAT_ID]))
async def get_image_ig(message : Message, state : FSMContext):
    await images.add(file_id=message.photo[0].file_id, file_name=message.caption)
    await state.clear()
    await message.answer(text=f'Сохранил')