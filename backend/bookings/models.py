from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import RangeOperators
from django.core.validators import FileExtensionValidator
from django.db import DEFAULT_DB_ALIAS, models
from django.db.models import F, Func, Q

from core.choices import Currency
from core.constants import SYSTEM_BASE_CURRENCY
from core.models import BaseModel
from core.file_processing import FileProcessOptions, FileProcessingMixin
from core.services import ALLOWED_UPLOAD_EXTENSIONS
from fleet.models import Car
from properties.models import House


class BookingStatus(models.TextChoices):
    CONFIRMED = 'CONFIRMED', 'Confirmed'
    # PARTIALLY_PAID = 'PARTIALLY_PAID', 'Partially paid'
    # PAID = 'PAID', 'Paid'
    # COMPLETED = 'COMPLETED', 'Completed'
    CANCELLED = 'CANCELLED', 'Cancelled'


class Renter(FileProcessingMixin, models.Model):
    FILE_FIELDS = {
        'document': FileProcessOptions(
            max_side=1600,
            quality=75,
        ),
    }

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
                allowed_extensions=[
                    e.lstrip('.')
                    for e in ALLOWED_UPLOAD_EXTENSIONS
                ]
            ),
        ],
    )

    class Meta:
        verbose_name = 'Renter'
        verbose_name_plural = 'Renters'
        ordering = ['last_name', 'first_name']

    def __str__(self) -> str:
        return f'{self.last_name} {self.first_name}'


class AbstractBooking(FileProcessingMixin, BaseModel):
    SKIP_PRECHECK_CONSTRAINTS = set()

    FILE_FIELDS = {
        'contract': FileProcessOptions(
            max_side=1600,
            quality=75,
        ),
    }

    renter = models.ForeignKey(
        Renter,
        on_delete=models.PROTECT,
        related_name='%(class)ss',
        verbose_name='Renter',
    )
    start_date = models.DateField(verbose_name='Start date')
    end_date = models.DateField(verbose_name='End date')
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
                allowed_extensions=[
                    e.lstrip('.')
                    for e in ALLOWED_UPLOAD_EXTENSIONS
                ]
            ),
        ],
    )

    class Meta:
        abstract = True

    @classmethod
    def build_no_overlap_constraint(
        cls, unit_field: str, name: str
    ) -> ExclusionConstraint:
        """
        unit_field: имя FK-поля ресурса ('car', 'house', ...)
        name: уникальное имя constraints
        """
        return ExclusionConstraint(
            name=name,
            expressions=[
                (unit_field, RangeOperators.EQUAL),
                (
                    Func(
                        F('start_date'),
                        F('end_date'),
                        function='daterange',
                        template="%(function)s(%(expressions)s, '[]')",
                    ),
                    RangeOperators.OVERLAPS,
                ),
            ],
            condition=~Q(status=BookingStatus.CANCELLED),
        )

    def validate_constraints(self, exclude=None):
        constraints = [
            c for c in self._meta.constraints
            if c.name not in self.SKIP_PRECHECK_CONSTRAINTS
        ]
        using = DEFAULT_DB_ALIAS
        for constraint in constraints:
            constraint.validate(
                model=self.__class__,
                instance=self,
                exclude=exclude,
                using=using,
            )

    def get_overlap_queryset(self):
        raise NotImplementedError

    def get_overlap_unit_filter(self):
        raise NotImplementedError

    def validate_domain_specific(self):
        pass

    def clean(self):
        from .services import (
            validate_date_range,
            validate_no_overlaps,
        )

        if not self.start_date or not self.end_date:
            return

        validate_date_range(self.start_date, self.end_date)

        unit_filter = self.get_overlap_unit_filter()
        if not unit_filter:
            return

        validate_no_overlaps(
            queryset=self.get_overlap_queryset(),
            unit_filter=unit_filter,
            start_date=self.start_date,
            end_date=self.end_date,
            exclude_booking_id=self.pk,
            excluded_statuses=[BookingStatus.CANCELLED],
        )

        self.validate_domain_specific()


class Booking(AbstractBooking):
    SKIP_PRECHECK_CONSTRAINTS = {'booking_no_overlaps_per_car'}

    car = models.ForeignKey(
        Car,
        on_delete=models.PROTECT,
        related_name='bookings',
        verbose_name='Car',
    )
    start_mileage = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Start mileage',
    )
    end_mileage = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='End mileage',
    )

    class Meta:
        verbose_name = 'Car booking'
        verbose_name_plural = 'Car bookings'
        constraints = [
            AbstractBooking.build_no_overlap_constraint(
                unit_field='car',
                name='booking_no_overlaps_per_car',
            ),
        ]

    def __str__(self) -> str:
        start = (
            self.start_date.strftime('%d %b %y') if self.start_date else '—'
        )
        end = self.end_date.strftime('%d %b %y') if self.end_date else '—'
        dates = f'{start}–{end}'
        return f'{self.car} - {self.renter} ({dates})'

    def get_overlap_queryset(self):
        return Booking.objects.all()

    def get_overlap_unit_filter(self):
        if not self.car_id:
            return {}
        return {'car_id': self.car_id}

    def validate_domain_specific(self):
        from .services import validate_car_is_active, validate_mileage_range

        validate_mileage_range(self.start_mileage, self.end_mileage)
        validate_car_is_active(self.car_id)


class HouseBooking(AbstractBooking):
    SKIP_PRECHECK_CONSTRAINTS = {'house_booking_no_overlaps'}

    house = models.ForeignKey(
        House,
        on_delete=models.PROTECT,
        related_name='bookings',
        verbose_name='House',
    )

    class Meta:
        verbose_name = 'House booking'
        verbose_name_plural = 'House bookings'
        constraints = [
            AbstractBooking.build_no_overlap_constraint(
                unit_field='house',
                name='house_booking_no_overlaps',
            ),
        ]

    def __str__(self) -> str:
        start = (
            self.start_date.strftime('%d %b %y') if self.start_date else '—'
        )
        end = self.end_date.strftime('%d %b %y') if self.end_date else '—'
        dates = f'{start}–{end}'
        return f'{self.house} - {self.renter} ({dates})'

    def get_overlap_queryset(self):
        return HouseBooking.objects.all()

    def get_overlap_unit_filter(self):
        if not self.house_id:
            return {}
        return {'house_id': self.house_id}

    def validate_domain_specific(self):
        from .services import validate_house_is_active

        validate_house_is_active(self.house_id)
