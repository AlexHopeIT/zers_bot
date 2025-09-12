import os


WORKS_DIR = '../app/content/our_works/'
MESSAGE_MAX_LENGTH = 4096


def split_message(text: str, max_length: int = MESSAGE_MAX_LENGTH):
    """Разбивает текст на части, чтобы каждая часть не превышала max_length."""
    if len(text) <= max_length:
        return [text]

    parts = []
    while text:
        if len(text) <= max_length:
            parts.append(text)
            break

        split_point = text.rfind('.', 0, max_length)
        if split_point == -1:
            split_point = text.rfind(' ', 0, max_length)
        if split_point == -1:
            split_point = max_length

        parts.append(text[:split_point])
        text = text[split_point:].strip()

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
