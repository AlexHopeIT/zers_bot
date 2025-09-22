from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from create_db import toggle_request_status
from config import ADMINS
from keyboards.inline_kbs import (
    get_admin_menu_keyboard, get_requests_keyboard,
    )
from states.states import AdminState
from utils import (get_all_requests, get_answered_requests,
                   get_unanswered_requests
                   )

admin_router = Router()


@admin_router.message(F.from_user.id.in_(ADMINS), F.text == '/admin')
async def show_admin_panel(message: types.Message):
    keyboard = await get_admin_menu_keyboard()
    await message.answer('Вы в админ-панели!', reply_markup=keyboard)


@admin_router.callback_query(F.data.startswith((
        'show_all_requests_',
        'show_unanswered_requests_',
        'show_answered_requests_'
        )))
async def show_requests(callback: types.CallbackQuery):
    await callback.answer()

    data_parts = callback.data.split('_')
    filter_type = data_parts[1]
    page = int(data_parts[-1])

    if filter_type == 'all':
        requests = await get_all_requests()
    elif filter_type == 'unanswered':
        requests = await get_unanswered_requests()
    elif filter_type == 'answered':
        requests = await get_answered_requests()

    if not requests:
        keyboard = await get_admin_menu_keyboard()
        await callback.message.edit_text(
            'На данный момент заявок нет',
            reply_markup=keyboard
        )
        return

    requests_per_page = 5
    total_pages = (
        len(requests) + requests_per_page - 1
        ) // requests_per_page
    start_index = (page - 1) * requests_per_page
    end_index = start_index + requests_per_page
    current_requests = requests[start_index:end_index]

    text = f'📋 **Заявки (Страница {page}/{total_pages})**:\n\n'
    for req in current_requests:
        status = '✅ Отвечено' if req.answered else '⏳ В ожидании'
        text += (
            f'**ID:** `{req.id}`\n'
            f'**Статус:** {status}\n'
            f'**Имя:** {req.name}\n'
            f'**Сообщение:** `{req.message[:50]}...`\n'
            f'**Дата:** {req.created_at.strftime("%Y-%m-%d %H:%M")}\n'
        )
        text += '-' * 10 + '\n\n'

    keyboard = get_requests_keyboard(
        current_requests, page, total_pages, filter_type
    )
    await callback.message.edit_text(
        text, reply_markup=keyboard, parse_mode='Markdown'
    )


@admin_router.callback_query(F.data.startswith('toggle_answered_'))
async def toggle_request_status_handler(callback: types.CallbackQuery):
    await callback.answer()
    
    parts = callback.data.split('_')
    request_id = int(parts[-2])
    new_status = parts[-1] == 'true'

    await toggle_request_status(request_id, new_status)
    
    await callback.message.edit_text(
        'Статус заявки изменен.',
        reply_markup=await get_admin_menu_keyboard()
        )


@admin_router.callback_query(F.data == 'admin_menu')
async def back_to_admin_menu(callback: types.CallbackQuery):
    await callback.answer()
    keyboard = await get_admin_menu_keyboard()
    await callback.message.edit_text(
        'Вы в админ-панели!', reply_markup=keyboard
        )
