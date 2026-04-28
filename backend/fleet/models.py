from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.validators import FileExtensionValidator
from django.db import models

from core.models import BaseModel
from core.services import (
    ALLOWED_UPLOAD_EXTENSIONS,
    IMAGE_EXTENSIONS,
    process_uploaded_file,
)

User = get_user_model()


class Car(BaseModel):
    name = models.CharField(
        max_length=255,
        verbose_name='Name',
    )
    plate_number = models.CharField(
        max_length=32,
        unique=True,
        verbose_name='License plate',
    )
    owners = models.ManyToManyField(
        User,
        related_name='cars',
        verbose_name='Owners',
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Active',
    )
    avatar = models.FileField(
        upload_to='cars/avatars/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='Avatar',
        validators=[
            FileExtensionValidator(
                allowed_extensions=[e.lstrip('.') for e in IMAGE_EXTENSIONS]
            ),
        ],
    )

    class Meta:
        verbose_name = 'Car'
        verbose_name_plural = 'Cars'

    def __str__(self) -> str:
        return f'{self.name}'

    def save(self, *args, **kwargs):
        if self.avatar and self.avatar.name:
            try:
                raw = self.avatar.read()
                if raw:
                    content, name = process_uploaded_file(
                        raw,
                        self.avatar.name,
                        max_side=1600,
                        quality=75,
                    )
                    self.avatar.save(name, ContentFile(content), save=False)
            except Exception:
                pass
        super().save(*args, **kwargs)


class CarInspection(models.Model):
    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name='inspections',
        verbose_name='Car',
    )
    date = models.DateField(verbose_name='Inspection date')
    place = models.CharField(
        max_length=255,
        verbose_name='Place',
        blank=True,
    )
    comment = models.TextField(
        verbose_name='Comment',
        blank=True,
    )

    class Meta:
        verbose_name = 'Car inspection'
        verbose_name_plural = 'Car inspections'
        ordering = ['-date']

    def __str__(self):
        return f'{self.car} — {self.date}'


class InsuranceCompany(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name='Name',
        unique=True,
    )

    class Meta:
        verbose_name = 'Insurance company'
        verbose_name_plural = 'Insurance companies'
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class CarInsurance(models.Model):
    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name='insurances',
        verbose_name='Car',
    )
    insurer = models.ForeignKey(
        InsuranceCompany,
        on_delete=models.PROTECT,
        related_name='car_insurances',
        verbose_name='Insurance company',
    )
    policy_number = models.CharField(
        max_length=64,
        verbose_name='Policy number',
    )
    start_date = models.DateField(
        verbose_name='Start date',
    )
    end_date = models.DateField(
        verbose_name='End date',
    )

    class Meta:
        verbose_name = 'Car insurance'
        verbose_name_plural = 'Car insurances'
        ordering = ['-start_date']

    def __str__(self) -> str:
        return f'{self.insurer} — {self.policy_number} ({self.car})'


class CarInsuranceDocument(models.Model):
    insurance = models.ForeignKey(
        CarInsurance,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name='Car insurance',
    )
    doc_type = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Document type',
    )
    file = models.FileField(
        upload_to='insurances/%Y/%m/',
        verbose_name='Attachment',
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
        verbose_name = 'Insurance attachment'
        verbose_name_plural = 'Insurance attachments'

    def __str__(self) -> str:
        label = self.doc_type or 'Attachment'
        return f'{label} for insurance #{self.insurance_id}'

    def save(self, *args, **kwargs):
        if self.file and self.file.name:
            name_lower = self.file.name.lower()
            if any(name_lower.endswith(ext) for ext in IMAGE_EXTENSIONS):
                try:
                    raw = self.file.read()
                    if raw:
                        content, name = process_uploaded_file(
                            raw,
                            self.file.name,
                            max_side=1600,
                            quality=75,
                        )
                        self.file.save(name, ContentFile(content), save=False)
                except Exception:
                    pass
        super().save(*args, **kwargs)


class CarPhoto(models.Model):
    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name='Car',
    )
    photo = models.FileField(
        upload_to='cars/%Y/%m/',
        verbose_name='Attachment',
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
        verbose_name = 'Car attachment'
        verbose_name_plural = 'Car attachments'

    def __str__(self) -> str:
        return f'Attachment for car #{self.car_id}'

    def save(self, *args, **kwargs):
        if self.photo:
            try:
                raw = self.photo.read()
                if raw:
                    content, name = process_uploaded_file(
                        raw,
                        self.photo.name,
                        max_side=1600,
                        quality=75,
                    )
                    self.photo.save(name, ContentFile(content), save=False)
            except Exception:
                pass
        super().save(*args, **kwargs)
