from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext

from utils import get_work_data, our_works_dir_scan


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
        text='Проектным институтам',
        callback_data='design_institutes'
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
