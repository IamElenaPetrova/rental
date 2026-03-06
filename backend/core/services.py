"""
Обработка загрузок: сжатие изображений, остальные файлы без изменений.
S3-совместимо, без .path и файловой системы.
"""  # noqa: E501
from io import BytesIO

from PIL import Image

# Расширения изображений — сжимаем (max_side, quality)
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp')

# Все разрешённые расширения (для валидации в моделях): изображения + документы
ALLOWED_UPLOAD_EXTENSIONS = (
    '.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp',
    '.pdf', '.doc', '.docx',
)


def compress_image_bytes(image_bytes, max_side=1600, quality=75):
    """
    Сжимает изображение из bytes.
    Возвращает (bytes JPEG, True) или (исходные bytes, False).
    """
    try:
        img = Image.open(BytesIO(image_bytes))
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        w, h = img.size
        if w > max_side or h > max_side:
            ratio = min(max_side / w, max_side / h)
            new_size = (int(w * ratio), int(h * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        out = BytesIO()
        img.save(out, format='JPEG', quality=quality, optimize=True)
        return out.getvalue(), True
    except Exception:
        return image_bytes, False


def process_uploaded_file(file_bytes, filename, max_side=1600, quality=75):
    """
    Изображения сжимает, остальные типы без изменений.
    Возвращает (bytes для сохранения, новое имя файла).
    """
    if not file_bytes:
        return file_bytes, filename or ''

    ext = ''
    if filename:
        idx = filename.rfind('.')
        ext = ('.' + filename[idx + 1:].lower()) if idx != -1 else ''

    if ext in IMAGE_EXTENSIONS:
        compressed, ok = compress_image_bytes(
            file_bytes, max_side=max_side, quality=quality
        )
        if ok:
            base = (
                filename[:filename.rfind('.')]
                if '.' in filename
                else (filename or 'photo')
            )
            return compressed, base + '.jpg'
    return file_bytes, filename or 'document'
