from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.db import models

from core.file_processing import FileProcessOptions, FileProcessingMixin
from core.models import BaseModel
from core.services import ALLOWED_UPLOAD_EXTENSIONS, IMAGE_EXTENSIONS

User = get_user_model()


class House(FileProcessingMixin, BaseModel):
    FILE_FIELDS = {
        'avatar': FileProcessOptions(max_side=1600, quality=75),
    }

    name = models.CharField(
        max_length=255,
        verbose_name='Name',
    )
    address = models.CharField(
        max_length=512,
        verbose_name='Address',
    )
    owners = models.ManyToManyField(
        User,
        related_name='houses',
        verbose_name='Owners',
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Active',
    )
    comment = models.TextField(
        verbose_name='Comment',
        blank=True,
    )
    avatar = models.FileField(
        upload_to='houses/avatars/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='Avatar',
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    e.lstrip('.') for e in IMAGE_EXTENSIONS
                ]
            ),
        ],
    )

    class Meta:
        verbose_name = 'House'
        verbose_name_plural = 'Houses'
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class HousePhoto(FileProcessingMixin, models.Model):
    FILE_FIELDS = {
        'photo': FileProcessOptions(
            max_side=1600,
            quality=75,
        ),
    }

    house = models.ForeignKey(
        House,
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name='House',
    )
    sort_order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='Sort order',
        help_text='Lower numbers appear first in the gallery.',
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Description',
    )
    photo = models.FileField(
        upload_to='houses/gallery/%Y/%m/',
        verbose_name='Photo',
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    e.lstrip('.') for e in IMAGE_EXTENSIONS
                ]
            ),
        ],
    )

    class Meta:
        verbose_name = 'House gallery photo'
        verbose_name_plural = 'House gallery photos'
        ordering = ['sort_order', 'id']

    def __str__(self) -> str:
        label = (self.description or '').strip()
        if label:
            return f'{label} (house #{self.house_id})'
        if self.pk:
            return f'Gallery photo #{self.pk} (house #{self.house_id})'
        return f'Gallery photo (house #{self.house_id})'


class HouseDocument(FileProcessingMixin, models.Model):
    FILE_FIELDS = {
        'file': FileProcessOptions(max_side=1600, quality=75),
    }

    house = models.ForeignKey(
        House,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name='House',
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Description',
    )
    file = models.FileField(
        upload_to='houses/documents/%Y/%m/',
        verbose_name='File',
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    e.lstrip('.')
                    for e in ALLOWED_UPLOAD_EXTENSIONS
                ]
            ),
        ],
    )

    class Meta:
        verbose_name = 'House document'
        verbose_name_plural = 'House documents'
        ordering = ['-id']

    def __str__(self) -> str:
        label = (self.description or '').strip() or 'Document'
        return f'{label} (house #{self.house_id})'
