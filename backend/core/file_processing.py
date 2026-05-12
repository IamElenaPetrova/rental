import logging
from dataclasses import dataclass
from typing import Dict

from django.core.files.base import ContentFile

from core.services import IMAGE_EXTENSIONS, process_uploaded_file

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class FileProcessOptions:
    images_only: bool = False
    max_side: int = 1600
    quality: int = 75


class FileProcessingMixin:
    FILE_FIELDS: Dict[str, FileProcessOptions] = {}

    # ------------------------
    # Проверка: файл валиден?
    # ------------------------
    def _should_process_field(self, field_file, options: FileProcessOptions) -> bool:
        if not field_file or not getattr(field_file, "name", ""):
            return False

        if not options.images_only:
            return True

        name_lower = field_file.name.lower()
        return any(name_lower.endswith(ext) for ext in IMAGE_EXTENSIONS)

    # ------------------------
    # Проверка: файл изменился?
    # ------------------------
    def _is_file_changed(self, field_name: str) -> bool:
        # Новый объект → всегда обрабатываем
        if not self.pk:
            return True

        # Получаем старое имя файла без загрузки всей модели
        old_name = (
            self.__class__.objects
            .filter(pk=self.pk)
            .values_list(field_name, flat=True)
            .first()
        )

        new_file = getattr(self, field_name, None)

        if not new_file:
            return False

        # Если имя изменилось → файл новый
        return old_name != new_file.name

    # ------------------------
    # Обработка одного поля
    # ------------------------
    def _process_single_field(self, field_name: str, options: FileProcessOptions) -> None:
        field_file = getattr(self, field_name, None)

        if not self._should_process_field(field_file, options):
            return

        if not self._is_file_changed(field_name):
            return

        try:
            raw = field_file.read()
            if not raw:
                return

            content, new_name = process_uploaded_file(
                raw,
                field_file.name,
                max_side=options.max_side,
                quality=options.quality,
            )

            field_file.save(new_name, ContentFile(content), save=False)

        except Exception:
            logger.exception(
                "Failed to process file field '%s' for %s(pk=%s)",
                field_name,
                self.__class__.__name__,
                getattr(self, "pk", None),
            )

    # ------------------------
    # Обработка всех полей
    # ------------------------
    def _preprocess_files(self) -> None:
        for field_name, options in self.FILE_FIELDS.items():
            self._process_single_field(field_name, options)

    # ------------------------
    # Save
    # ------------------------
    def save(self, *args, **kwargs):
        self._preprocess_files()
        return super().save(*args, **kwargs)