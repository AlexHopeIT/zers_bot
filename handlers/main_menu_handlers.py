import os
from aiogram import Router, types, F
from aiogram.exceptions import TelegramBadRequest, TelegramAPIError
from aiogram.fsm.context import FSMContext
from keyboards.inline_kbs import (
    main_menu_keyboard, our_works_keyboard, back_to_works_keyboard,
    faq_keyboard, back_to_faq_keyboard
    )
from utils import (
    get_work_data, our_works_dir_scan, split_message, send_or_edit_long_message
    )
from content.faq.texts import (
    GENERAL_QUESTIONS, GARDENING_AND_PARK, SPORT, ARCHITECTURAL_AND_ARTISTIC,
    INDUSTRIAL, STREET, INSIDE
    )
from states.states import LeaveARequestState
from create_db import Applications, AsyncSessionLocal

main_menu_router = Router()


@main_menu_router.callback_query(
    F.data == 'main_menu_inline'
    )
async def main_menu_inline(callback: types.CallbackQuery):
    await callback.answer()
    keyboard = await main_menu_keyboard()
    await callback.message.edit_text(
        text='Выберете раздел',
        reply_markup=keyboard
    )


@main_menu_router.callback_query(
    F.data == 'contacts'
    )
async def contacts(
    callback: types.CallbackQuery
):
    await callback.answer()

    keyboard = await main_menu_keyboard()
    contacts_text = (
        '<b>📞 Наши контакты</b>\n\n'
        '<b>Офис:</b>\n'
        '🏢 <b>Адрес:</b> РОССИЯ, г. Новочеркасск, ул. Первомайская, 107А\n'
        '📞 <b>Телефон:</b> +7 863 303 3698\n'
        '🌐 <b>Сайт:</b> <a href="http://www.zers-group.ru">zers-group.ru</a>\n'
        '📧 <b>Почта:</b> <a href="mailto:zers@zers-group.ru">zers@zers-group.ru</a>\n'
        '⏰ <b>Режим работы:</b> пн-пт 09:00–18:00 (перерыв 13:00–14:00)\n\n'

        '<b>Мессенджеры:</b>\n'
        '📱 <a href="https://api.whatsapp.com/send?phone=79185443910">WhatsApp</a>\n\n'

        '<b>Руководство:</b>\n'
        '🟢 <b>Осипенко Ксения</b> — Генеральный директор\n'
        '  📧 <a href="mailto:trade@zers-group.ru">trade@zers-group.ru</a>\n'
        '  📞 Внутр. № 109\n'
        '🟢 <b>Реунов Максим</b> — Зам. генерального директора\n'
        '  📧 <a href="mailto:led@zers-group.ru">led@zers-group.ru</a>\n'
        '  📞 Внутр. № 107\n\n'

        '<b>Приемная:</b>\n'
        '🟢 <b>Амелина Кристина</b>\n'
        '  📧 <a href="mailto:zers@zers-group.ru">zers@zers-group.ru</a>\n'
        '  📞 Внутр. № 101\n\n'

        '<b>Проектный отдел:</b>\n'
        '🟢 <b>Игорь Левченко</b>\n'
        '  📧 <a href="mailto:svet@zers-group.ru">svet@zers-group.ru</a>\n'
        '  📞 Внутр. № 105\n\n'

        '<b>Реквизиты:</b>\n'
        'ООО "Церс Дизайн"\n'
        '<b>ИНН/КПП:</b> 6163142891 / 616301001\n'
        '<b>ОГРН:</b> 1156196061317\n'
        '<b>Р/с:</b> 40702810195250102743\n'
        '<b>Банк:</b> ФИЛИАЛ ЮЖНЫЙ ПАО БАНКА "ФК ОТКРЫТИЕ"\n'
        '<b>К/с:</b> 30101810560150000061\n'
        '<b>БИК:</b> 046015061\n'
    )

    await callback.message.edit_text(
        contacts_text, parse_mode='HTML',
        reply_markup=keyboard
    )


@main_menu_router.callback_query(
    F.data == 'our_works'
    )
async def show_works_list(callback: types.CallbackQuery):
    '''Показывает список "Наши работы"'''
    await callback.answer()

    keyboard = await our_works_keyboard()

    await callback.message.answer(
        '✨ Посмотрите примеры наших работ:',
        reply_markup=keyboard
    )


@main_menu_router.callback_query(
    F.data.startswith('works_page:')
    )
async def paginate_works(callback: types.CallbackQuery):
    '''Обрабатывает пагинацию списка работ'''
    await callback.answer()
    page = int(callback.data.split(':')[1])
    keyboard = await our_works_keyboard(page=page)
    await callback.message.edit_reply_markup(reply_markup=keyboard)


@main_menu_router.callback_query(
    F.data.startswith('show_work:')
    )
async def show_single_work(callback: types.CallbackQuery):
    await callback.answer()
    work_id = int(callback.data.split(':')[1])
    all_works_map = our_works_dir_scan()
    work_name = all_works_map.get(work_id)

    keyboard = back_to_works_keyboard()
    if not work_name:
        await callback.message.answer('Проект не найден.')
        return

    description, photos = get_work_data(work_name)

    if not photos:
        await callback.message.answer('Фотографии для этой работы не найдены.')
        return

    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except TelegramAPIError:
        pass

    is_description_long = len(description) > 1024
    caption = description if not is_description_long else None

    if len(photos) > 1:
        media_group = [
            types.InputMediaPhoto(
                media=types.FSInputFile(photos[0]), caption=caption
                )
        ]
        media_group.extend(
            [types.InputMediaPhoto(
                media=types.FSInputFile(p)
                ) for p in photos[1:]]
        )

        try:
            await callback.message.answer_media_group(media=media_group)
        except TelegramBadRequest:
            await callback.message.answer(
                'Произошла ошибка при отправке фотографий.'
                )
    else:
        photo = types.FSInputFile(photos[0])
        await callback.message.answer_photo(photo, caption=caption)

    if description and (
        is_description_long or (len(photos) == 1 and not description)
            ):

        desc_parts = split_message(description)
        for part in desc_parts:
            await callback.message.answer(text=part)

    await callback.message.answer('.', reply_markup=keyboard)


@main_menu_router.callback_query(F.data == 'company')
async def company_info(callback: types.CallbackQuery):
    await callback.answer()

    info_path = '../app/content/company/about_us.txt'

    if not os.path.exists(info_path):
        await callback.message.answer('Информация о компании не найдена.')
        return

    with open(info_path, 'r', encoding='utf-8') as f:
        company_info_full = f.read()

    keyboard = await main_menu_keyboard()
    await send_or_edit_long_message(
        callback,
        company_info_full,
        keyboard
    )


@main_menu_router.callback_query(
    F.data == 'faq'
    )
async def faq(callback: types.CallbackQuery):
    await callback.answer()
    keyboard = await faq_keyboard()
    await callback.message.edit_text(
        '📌 Выберете категорию:',
        reply_markup=keyboard
    )


@main_menu_router.callback_query(
    F.data == 'general_questions'
    )
async def general_questions(callback: types.CallbackQuery):
    await callback.answer()
    keyboard = back_to_faq_keyboard()
    await send_or_edit_long_message(
        callback,
        GENERAL_QUESTIONS,
        keyboard
    )


@main_menu_router.callback_query(
    F.data == 'gardening_and_park'
    )
async def gardening_and_park(callback: types.CallbackQuery):
    await callback.answer()
    keyboard = back_to_faq_keyboard()
    await send_or_edit_long_message(
        callback,
        GARDENING_AND_PARK,
        keyboard
    )


@main_menu_router.callback_query(
    F.data == 'sport'
    )
async def sport(callback: types.CallbackQuery):
    await callback.answer()
    keyboard = back_to_faq_keyboard()
    await send_or_edit_long_message(
        callback,
        SPORT,
        keyboard
    )


@main_menu_router.callback_query(
    F.data == 'architectural_and_artistic'
    )
async def architectural_and_artistic(callback: types.CallbackQuery):
    await callback.answer()
    keyboard = back_to_faq_keyboard()
    await send_or_edit_long_message(
        callback,
        ARCHITECTURAL_AND_ARTISTIC,
        keyboard
    )


@main_menu_router.callback_query(
    F.data == 'industrial'
    )
async def industrial(callback: types.CallbackQuery):
    await callback.answer()
    keyboard = back_to_faq_keyboard()
    await send_or_edit_long_message(
        callback,
        INDUSTRIAL,
        keyboard
    )


@main_menu_router.callback_query(
    F.data == 'street'
    )
async def street(callback: types.CallbackQuery):
    await callback.answer()
    keyboard = back_to_faq_keyboard()
    await send_or_edit_long_message(
        callback,
        STREET,
        keyboard
    )


@main_menu_router.callback_query(
    F.data == 'inside'
    )
async def inside(callback: types.CallbackQuery):
    await callback.answer()
    keyboard = back_to_faq_keyboard()
    await send_or_edit_long_message(
        callback,
        INSIDE,
        keyboard
    )
