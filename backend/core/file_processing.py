import logging
from dataclasses import dataclass
from typing import Dict, Tuple

from django.core.files.base import ContentFile

from core.services import IMAGE_EXTENSIONS, process_uploaded_file

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class FileProcessOptions:
    max_side: int = 1600
    quality: int = 75
    # Когда появится сжатие PDF: True на поле + ветка в preprocess_upload
    compress_pdf: bool = False


def _extension_from_filename(filename: str) -> str:
    if not filename:
        return ""
    idx = filename.rfind(".")
    return ("." + filename[idx + 1:].lower()) if idx != -1 else ""


def preprocess_upload(
    file_bytes: bytes,
    filename: str,
    *,
    max_side: int = 1600,
    quality: int = 75,
) -> Tuple[bytes, str]:
    """
    Единая точка преобразования загрузки перед сохранением в FileField.
    Сейчас: делегирование в process_uploaded_file (картинки — сжатие, остальное — как есть).
    Позже: сюда же ветку для PDF/DOC при необходимости.
    """
    return process_uploaded_file(
        file_bytes, filename, max_side=max_side, quality=quality
    )


class FileProcessingMixin:
    FILE_FIELDS: Dict[str, FileProcessOptions] = {}

    def _field_has_file(self, field_file) -> bool:
        return bool(field_file and getattr(field_file, "name", ""))

    def _needs_in_memory_preprocess(
        self, filename: str, options: FileProcessOptions
    ) -> bool:
        ext = _extension_from_filename(filename)
        if ext in IMAGE_EXTENSIONS:
            return True
        if options.compress_pdf and ext == ".pdf":
            return True
        return False

    def _is_file_changed(self, field_name: str) -> bool:
        if not self.pk:
            return True

        old_name = (
            self.__class__.objects.filter(pk=self.pk)
            .values_list(field_name, flat=True)
            .first()
        )

        new_file = getattr(self, field_name, None)

        if not new_file:
            return False

        return old_name != new_file.name

    def _process_single_field(
        self, field_name: str, options: FileProcessOptions
    ) -> None:
        field_file = getattr(self, field_name, None)

        if not self._field_has_file(field_file):
            return

        if not self._is_file_changed(field_name):
            return

        if not self._needs_in_memory_preprocess(field_file.name, options):
            # PDF/DOC и т.д.: process_uploaded_file всё равно не меняет их —
            # не читаем файл в память для препроцессинга.
            return

        try:
            raw = field_file.read()
            if not raw:
                return

            content, new_name = preprocess_upload(
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

    def _preprocess_files(self) -> None:
        for field_name, options in self.FILE_FIELDS.items():
            self._process_single_field(field_name, options)

    def save(self, *args, **kwargs):
        self._preprocess_files()
        return super().save(*args, **kwargs)