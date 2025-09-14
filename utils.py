import os
import re
from aiogram.types import CallbackQuery, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramAPIError
from states.states import LeaveARequestState


WORKS_DIR = '../app/content/our_works/'
MESSAGE_MAX_LENGTH = 4096


def split_message(text: str, max_length: int = 4096) -> list[str]:
    """
    Разбивает длинное HTML-сообщение на части, сохраняя целостность тегов.
    """
    parts = []

    # Регулярное выражение для поиска всех HTML-тегов
    tags_regex = re.compile(r'</?([a-z])>')

    current_part = ''
    open_tags = []

    # Разбиваем текст по строкам, чтобы избежать разрыва слов
    lines = text.split('\n')

    for line in lines:
        temp_part = current_part + '\n' + line if current_part else line

        if len(temp_part) > max_length:
            # Перед отправкой закрываем все открытые теги
            for tag in reversed(open_tags):
                current_part += f'</{tag}>'
            parts.append(current_part)

            # Начинаем новую часть, заново открывая теги
            current_part = ''
            for tag in open_tags:
                current_part += f'<{tag}>'
            current_part += line
        else:
            current_part = temp_part

        # Обновляем список открытых тегов
        for match in tags_regex.finditer(line):
            tag_name = match.group(1)
            if match.group(0).startswith('</'):
                if tag_name in open_tags:
                    open_tags.remove(tag_name)
            else:
                open_tags.append(tag_name)

    if current_part:
        # Добавляем последнюю часть и закрываем оставшиеся теги
        for tag in reversed(open_tags):
            current_part += f'</{tag}>'
        parts.append(current_part)

    return parts


def our_works_dir_scan():
    works_map = {}
    if not os.path.exists(WORKS_DIR):
        return works_map

    # Используем enumerate() для создания числового ID для каждого проекта
    for i, work_name in enumerate(os.listdir(WORKS_DIR)):
        if os.path.isdir(os.path.join(WORKS_DIR, work_name)):
            works_map[i] = work_name

    return works_map


def get_work_data(work_name: str):
    '''
    Получает фотографии и описание для конкретного проекта.
    Возвращает кортеж: (описание, [путь_к_фото1, путь_к_фото2, ...])
    '''
    work_path = os.path.join(WORKS_DIR, work_name)
    if not os.path.exists(work_path):
        return None, []

    description_path = os.path.join(work_path, 'description.txt')
    description = ''
    if os.path.exists(description_path):
        with open(description_path, 'r', encoding='utf-8') as f:
            description = f.read()

    photos = [
        os.path.join(
            work_path, f
            ) for f in os.listdir(work_path) if f.endswith(
                ('jpg', 'jpeg', 'png')
                )
        ]
    return description, photos


async def send_or_edit_long_message(
    callback: CallbackQuery,
    text: str,
    keyboard: InlineKeyboardMarkup
):
    """
    Отправляет или редактирует сообщение с длинным текстом.

    Если текст слишком длинный для одного сообщения, он разбивается на части и
    отправляется последовательно. В противном случае сообщение редактируется.
    """
    text_parts = split_message(text)

    if len(text_parts) == 1:
        # Если текст короткий, пытаемся отредактировать сообщение
        try:
            await callback.message.edit_text(
                text=text_parts[0],
                reply_markup=keyboard,
                parse_mode='HTML'
            )
        except TelegramAPIError:
            # Если редактирование не удалось, отправляем новое сообщение
            await callback.message.answer(
                text=text_parts[0],
                reply_markup=keyboard,
                parse_mode='HTML'
            )
    else:
        # Если текст длинный, отправляем несколько сообщений
        try:
            # Сначала убираем клавиатуру из старого сообщения
            await callback.message.edit_reply_markup(reply_markup=None)
        except TelegramAPIError:
            pass

        # Отправляем каждую часть текста
        for part in text_parts:
            await callback.message.answer(text=part, parse_mode='HTML')

        # Отправляем клавиатуру в самом конце
        await callback.message.answer('.', reply_markup=keyboard)
