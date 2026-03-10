from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.validators import FileExtensionValidator
from django.db import models

from core.constants import SYSTEM_BASE_CURRENCY
from core.models import BaseModel
from core.services import ALLOWED_UPLOAD_EXTENSIONS, process_uploaded_file
from fleet.models import Car


class BookingStatus(models.TextChoices):
    CONFIRMED = 'CONFIRMED', 'Confirmed'
    PARTIALLY_PAID = 'PARTIALLY_PAID', 'Partially paid'
    PAID = 'PAID', 'Paid'
    COMPLETED = 'COMPLETED', 'Completed'
    CANCELLED = 'CANCELLED', 'Cancelled'


class Currency(models.TextChoices):
    USD = 'USD', 'USD'
    PESO = 'PESO', 'PESO'


class Renter(models.Model):
    first_name = models.CharField(max_length=255, verbose_name='First name')
    last_name = models.CharField(max_length=255, verbose_name='Last name')
    phone = models.CharField(max_length=32, verbose_name='Phone')
    comment = models.TextField(verbose_name='Comment', blank=True)
    document = models.FileField(
        upload_to='renters/%Y/%m/',
        verbose_name='Document',
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=[e.lstrip('.') for e in ALLOWED_UPLOAD_EXTENSIONS]
            ),
        ],
    )

    class Meta:
        verbose_name = 'Renter'
        verbose_name_plural = 'Renters'
        ordering = ['last_name', 'first_name']

    def __str__(self) -> str:
        return f'{self.last_name} {self.first_name}'

    def save(self, *args, **kwargs):
        if self.document:
            try:
                raw = self.document.read()
                if raw:
                    content, name = process_uploaded_file(
                        raw, self.document.name, max_side=1600, quality=75
                    )
                    self.document.save(name, ContentFile(content), save=False)
            except Exception:
                pass
        super().save(*args, **kwargs)


class Booking(BaseModel):
    car = models.ForeignKey(
        Car,
        on_delete=models.PROTECT,
        related_name='bookings',
        verbose_name='Car',
    )
    renter = models.ForeignKey(
        Renter,
        on_delete=models.PROTECT,
        related_name='bookings',
        verbose_name='Renter',
    )

    start_date = models.DateField(
        verbose_name='Start date',
    )
    end_date = models.DateField(
        verbose_name='End date',
    )

    rent_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Rent amount',
    )
    currency = models.CharField(
        max_length=4,
        choices=Currency.choices,
        default=SYSTEM_BASE_CURRENCY,
        verbose_name='Booking currency',
    )
    status = models.CharField(
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.CONFIRMED,
        verbose_name='Status',
    )
    comment = models.TextField(
        verbose_name='Comment',
        blank=True,
        null=True,
    )
    contract = models.FileField(
        upload_to='bookings/%Y/%m/',
        verbose_name='Contract',
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=[e.lstrip('.') for e in ALLOWED_UPLOAD_EXTENSIONS]
            ),
        ],
    )

    class Meta:
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'

    def __str__(self) -> str:
        start = self.start_date.strftime('%d %b %y') if self.start_date else '—'
        end = self.end_date.strftime('%d %b %y') if self.end_date else '—'
        dates = f'{start}–{end}'
        return f'{self.car} - {self.renter} ({dates})'

    def clean(self):
        from .services import (
            format_overlapping_bookings_message,
            get_overlapping_bookings,
        )

        if not self.car_id or not self.start_date or not self.end_date:
            return

        overlapping = get_overlapping_bookings(
            car=self.car,
            start_date=self.start_date,
            end_date=self.end_date,
            exclude_booking_id=self.pk,
        )
        if overlapping.exists():
            raise ValidationError(
                format_overlapping_bookings_message(overlapping)
            )

    def save(self, *args, **kwargs):
        if self.contract:
            try:
                raw = self.contract.read()
                if raw:
                    content, name = process_uploaded_file(
                        raw, self.contract.name, max_side=1600, quality=75
                    )
                    self.contract.save(name, ContentFile(content), save=False)
            except Exception:
                pass
        super().save(*args, **kwargs)
