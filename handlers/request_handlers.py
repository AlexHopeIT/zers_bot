from aiogram import Bot, Router, types, F
from aiogram.fsm.context import FSMContext
from keyboards.inline_kbs import (
    main_menu_keyboard
    )
from states.states import LeaveARequestState
from create_db import Applications, AsyncSessionLocal
from config import CHAT_ID

request_router = Router()


@request_router.callback_query(F.data == 'leave_a_request')
async def start_request_process(
    callback: types.CallbackQuery, state: FSMContext
        ):
    await callback.answer()
    await callback.message.edit_text('Как к Вам обращаться?')
    await state.set_state(LeaveARequestState.waiting_for_name)


@request_router.message(LeaveARequestState.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer('Введите Ваш номер телефона')
    await state.set_state(LeaveARequestState.waiting_for_phone)


@request_router.message(LeaveARequestState.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    # Добавь здесь валидацию номера телефона, если нужно
    await state.update_data(phone=message.text)
    await message.answer('Введите Ваш адрес электронной почты')
    await state.set_state(LeaveARequestState.waiting_for_email)


@request_router.message(LeaveARequestState.waiting_for_email)
async def process_email(message: types.Message, state: FSMContext):
    await state.update_data(email=message.text)
    await message.answer('Напишите, с какой целью Вы оставляете заявку')
    await state.set_state(LeaveARequestState.waiting_for_message)


@request_router.message(LeaveARequestState.waiting_for_message)
async def process_message(
    message: types.Message, state: FSMContext, bot: Bot
        ):
    await state.update_data(request_text=message.text)

    user_data = await state.get_data()
    name = user_data.get('name')
    phone = user_data.get('phone')
    email = user_data.get('email')
    request_text = user_data.get('request_text')

    async with AsyncSessionLocal() as db:
        new_application = Applications(
            name=name,
            phone=phone,
            email=email,
            message=request_text
        )
        db.add(new_application)
        await db.commit()

    # Отправка уведомления в чат
    admin_notification_text = (
        f"**🔔 Новая заявка!**\n\n"
        f"**От кого:** {name}\n"
        f"**Телефон:** {phone}\n"
        f"**Email:** {email}\n\n"
        f"**Сообщение:**\n{request_text}"
    )

    await bot.send_message(
        chat_id=CHAT_ID,
        text=admin_notification_text,
        parse_mode="Markdown"
    )

    keyboard = await main_menu_keyboard()
    await message.answer(
        '✅ Ваша заявка отправлена. Мы скоро свяжемся с вами!',
        reply_markup=keyboard
        )

    # Очищаем состояние
    await state.clear()
