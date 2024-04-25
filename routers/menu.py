from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from models.keyboards import MenuKeyboards
from models.db import images
from models.seo_texts import start_command, contactus_command
from models.fsm import GiveIdState


router = Router()

@router.message(Command(commands=["start"]))
async def start(message : Message):
    m = await message.answer_photo(
        photo= await images.get_by_name('PhotoArtComplect'),
        caption=start_command, 
        reply_markup=MenuKeyboards.get_menu())

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

#save new image to db

@router.message(Command(commands=['save_image']))
async def save_image(message : Message, state : FSMContext):
    await state.set_state(GiveIdState.Recieve_image)
    await message.answer(text=f'Жду картинку, с подписью (названием файла)')

@router.message(GiveIdState.Recieve_image, F.photo)
async def get_image_ig(message : Message, state : FSMContext):
    await images.add(file_id=message.photo[-1].file_id, file_name=message.caption)
    await state.clear()
    await message.answer(text=f'Сохранил')