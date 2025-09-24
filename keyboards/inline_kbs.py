from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext

from utils import our_works_dir_scan
from content.services_data import SERVICES


async def main_menu_keyboard():
    '''Создает инлайн-клавиатуру главного меню'''
    builder = InlineKeyboardBuilder()

    builder.button(
        text='Услуги',
        callback_data='services'
    )
    builder.button(
        text='Продукция',
        callback_data='products'
    )
    builder.button(
        text='Наши работы',
        callback_data='our_works'
    )
    builder.button(
        text='О компании',
        callback_data='company'
    )
    builder.button(
        text='Контакты',
        callback_data='contacts'
    )
    builder.button(
        text='FAQ',
        callback_data='faq'
    )
    builder.button(
        text='Оставить заявку',
        callback_data='leave_a_request'
    )

    builder.adjust(2)
    return builder.as_markup()


async def our_works_keyboard(page: int = 0, per_page: int = 5):
    builder = InlineKeyboardBuilder()
    all_works_map = our_works_dir_scan()
    all_works_ids = list(all_works_map.keys())
    total_works = len(all_works_ids)

    start_index = page * per_page
    end_index = start_index + per_page

    current_ids = all_works_ids[start_index:end_index]

    for work_id in current_ids:
        builder.button(
            text=all_works_map[work_id],
            callback_data=f'show_work:{work_id}'
        )

    builder.adjust(1)

    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(
                text='⬅️ Назад', callback_data=f'works_page:{page -  1}'
            )
        )
    if end_index < total_works:
        nav_buttons.append(
            InlineKeyboardButton(
                text='Далее ➡️', callback_data=f'works_page:{page +  1}'
            )
        )
    if nav_buttons:
        builder.row(*nav_buttons)

    builder.row(InlineKeyboardButton(
        text='Ⓜ️ В главное меню', callback_data='main_menu_inline'
    ))
    return builder.as_markup()


def back_to_works_keyboard():
    """Создаёт клавиатуру с кнопкой 'Назад к списку работ'."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text='⬅️ Назад к списку работ',
        callback_data='our_works'
    )
    return builder.as_markup()


async def faq_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(
        text='Общие вопросы о светодиодном освещении территорий',
        callback_data='general_questions'
    )

    builder.button(
        text='Освещение садово-парковое',
        callback_data='gardening_and_park'
    )

    builder.button(
        text='Спортивное освещение (стадионы, площадки, фитнес-зоны)',
        callback_data='sport'
    )

    builder.button(
        text='Архитектурно-Художественное освещение (фасады, памятники)',
        callback_data='architectural_and_artistic'
    )

    builder.button(
        text='Промышленное освещение',
        callback_data='industrial'
    )

    builder.button(
        text='Уличное освещение',
        callback_data='street'
    )

    builder.button(
        text='Внутреннее освещение. Офисное и торговое',
        callback_data='inside'
    )

    builder.button(
        text='Ⓜ️ В главное меню',
        callback_data='main_menu_inline'
    )

    builder.adjust(1)
    return builder.as_markup()


def back_to_faq_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(
        text='Ⓜ️ В главное меню',
        callback_data='main_menu_inline'
    )
    builder.adjust(1, 2, 1)
    return builder.as_markup()


async def get_admin_menu_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(
        text='🔔 Показать все заявки',
        callback_data='show_all_requests_1'
    )
    builder.button(
        text='⏳ Неотвеченные',
        callback_data='show_unanswered_requests_1'
    )
    builder.button(
        text='✅ Отвеченные',
        callback_data='show_answered_requests_1'
    )
    builder.button(
        text='Ⓜ️ В главное меню',
        callback_data='main_menu_inline'
    )

    builder.adjust(1, 2, 1)
    return builder.as_markup()


def get_requests_keyboard(current_requests, page, total_pages, filter_type):
    nav_buttons = []
    if page > 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text='< Назад',
                callback_data=f'show_{filter_type}_requests_{page - 1}'
                )
                )
    if page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton(
                text='Вперёд >',
                callback_data=f'show_{filter_type}_requests_{page + 1}'
                )
                )

    back_button = [
        InlineKeyboardButton(
            text='◀️ Назад в админ-меню', callback_data='admin_menu'
            )
            ]

    request_buttons = []
    for req in current_requests:
        status_text = '✅ Отметить' if not req.answered else '❌ Снять отметку'
        request_buttons.append(
            [InlineKeyboardButton(
                text=f'{status_text} ID {req.id}',
                callback_data=f'toggle_answered_{req.id}_{"true" if not req.answered else "false"}'
            )]
        )

    return InlineKeyboardMarkup(
        inline_keyboard=[nav_buttons] + request_buttons + [back_button]
    )


async def services_keyboard():
    builder = InlineKeyboardBuilder()

    for service_id, service_info in SERVICES.items():
        builder.button(
            text=service_info['title'],
            callback_data=f'service_{service_id}'
        )
    builder.button(
        text='Ⓜ️ В главное меню',
        callback_data='main_menu_inline'
    )
    builder.adjust(1)
    return builder.as_markup()
