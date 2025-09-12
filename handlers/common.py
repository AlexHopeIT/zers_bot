from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from keyboards.inline_kbs import main_menu_keyboard


common_router = Router()


@common_router.message(CommandStart)
async def cmd_start(message: types.Message):
    keyboard = await main_menu_keyboard()
    await message.answer(
        f'Здравствуйте, {message.from_user.first_name}!👋\n'
        'Вас приветствует бот компании Церс - лидера среди '
        'российских производителей светодиодных светильников!\n',
        reply_markup=keyboard
    )
