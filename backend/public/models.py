from django.core.validators import FileExtensionValidator
from django.db import models

from core.file_processing import FileProcessOptions, FileProcessingMixin
from core.services import IMAGE_EXTENSIONS


class SiteSettings(FileProcessingMixin, models.Model):
    FILE_FIELDS = {
        'hero_image': FileProcessOptions(max_side=1920, quality=80),
    }

    hero_image = models.FileField(
        upload_to='site/hero/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='Homepage hero image',
        help_text='Wide photo for the main page (16:9 or 16:10 recommended).',
        validators=[
            FileExtensionValidator(
                allowed_extensions=[e.lstrip('.') for e in IMAGE_EXTENSIONS]
            ),
        ],
    )

    class Meta:
        verbose_name = 'Site settings'
        verbose_name_plural = 'Site settings'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self) -> str:
        return 'Homepage'
