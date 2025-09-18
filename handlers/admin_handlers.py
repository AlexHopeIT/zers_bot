from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from config import ADMINS
from keyboards.inline_kbs import get_admin_menu_keyboard

admin_router = Router()


@admin_router.message(F.from_user.id.in_(ADMINS), F.text == '/admin')
async def show_admin_panel(message: types.Message):
    keyboard = await get_admin_menu_keyboard()
    await message.answer('Вы в админ-панели!', reply_markup=keyboard)