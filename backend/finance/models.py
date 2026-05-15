from decimal import Decimal, ROUND_HALF_UP

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models

from bookings.models import Booking
from core.choices import Currency
from core.constants import SYSTEM_BASE_CURRENCY
from core.file_processing import FileProcessOptions, FileProcessingMixin
from core.models import BaseModel
from core.services import ALLOWED_UPLOAD_EXTENSIONS
from fleet.models import Car

User = get_user_model()


class AbstractIncome(BaseModel):
    """
    Payment against a booking (car or house).
    Booking FK lives on concrete models only (Income, HouseIncome).
    """

    received_date = models.DateField(
        verbose_name='Date received',
        null=True,
        blank=True,
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Payment amount',
    )
    currency = models.CharField(
        max_length=4,
        choices=Currency.choices,
        default=SYSTEM_BASE_CURRENCY,
        verbose_name='Payment currency',
    )
    exchange_rate = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        verbose_name='Rate',
        help_text=(
            'Payment curr. per 1 booking curr. (e.g. 60). '
            'Save to recalc.'
        ),
        null=True,
        blank=True,
    )
    amount_in_booking_currency = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Amount in booking currency',
        help_text=(
            'Calculated automatically on save using payment amount and rate.'
        ),
    )
    received_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='received_incomes',
        verbose_name='Payment recipient',
    )

    class Meta:
        abstract = True

    def validate_domain_specific(self):
        pass

    def get_contract_currency_for_validation(self):
        raise NotImplementedError

    def clean(self):
        from finance.services import validate_payment_currency

        super().clean()

        contract_currency = self.get_contract_currency_for_validation()
        if contract_currency is None:
            return

        validate_payment_currency(self, contract_currency)
        self.validate_domain_specific()

    def get_contract_currency(self) -> str:
        raise NotImplementedError

    def save(self, *args, **kwargs) -> None:
        from finance.services import apply_payment_currency

        apply_payment_currency(self, self.get_contract_currency())
        super().save(*args, **kwargs)


class Income(AbstractIncome):
    booking = models.ForeignKey(
        Booking,
        on_delete=models.PROTECT,
        related_name='incomes',
        verbose_name='Car Booking',
    )

    class Meta:
        db_table = 'finance_income'

    def __str__(self) -> str:
        return f'Income #{self.pk} for booking #{self.booking_id}'

    def get_contract_currency_for_validation(self):
        if not self.booking_id:
            return None
        return self.booking.currency

    def get_contract_currency(self) -> str:
        if not self.booking_id:
            raise ValidationError({'booking': 'Select a booking.'})
        return self.booking.currency

    def validate_domain_specific(self):
        if not self.booking_id:
            raise ValidationError({'booking': 'Select a booking.'})


class IncomeDocument(FileProcessingMixin, models.Model):
    FILE_FIELDS = {
        'file': FileProcessOptions(
            max_side=1600,
            quality=75,
        ),
    }

    income = models.ForeignKey(
        Income,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name='Payment',
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Description',
    )
    file = models.FileField(
        upload_to='incomes/%Y/%m/',
        verbose_name='File',
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    e.lstrip('.') for e in ALLOWED_UPLOAD_EXTENSIONS
                ]
            ),
        ],
    )

    class Meta:
        verbose_name = 'Payment document'
        verbose_name_plural = 'Payment documents'

    def __str__(self) -> str:
        return f'Document for payment #{self.income_id}'


class Expense(BaseModel):
    car = models.ForeignKey(
        Car,
        on_delete=models.PROTECT,
        related_name='expenses',
        verbose_name='Car',
    )
    description = models.TextField(
        verbose_name='Expense description',
    )
    date = models.DateField(
        verbose_name='Expense date',
    )
    payed_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='expenses_paid',
        verbose_name='Paid by',
        null=True,
        blank=True,
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Expense amount',
    )
    currency = models.CharField(
        max_length=4,
        choices=Currency.choices,
        default=SYSTEM_BASE_CURRENCY,
        verbose_name='Currency',
    )
    exchange_rate = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        verbose_name='Rate to base currency',
        help_text=(
            f'Leave empty for base currency ({SYSTEM_BASE_CURRENCY}) — '
            f'1 will be used on save. For other currencies: how much expense '
            f'currency for 1 unit of base currency (e.g. 60 when 1 '
            f'{SYSTEM_BASE_CURRENCY} = 60 PESO).'
        ),
        null=True,
        blank=True,
    )
    amount_in_base_currency = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Amount in base currency',
        help_text='Calculated automatically on save.',
        null=True,
        blank=True,
    )
    base_currency_at_save = models.CharField(
        max_length=4,
        default=SYSTEM_BASE_CURRENCY,
        verbose_name='Base currency at save time',
        help_text='Filled automatically on save.',
    )

    class Meta:
        verbose_name = 'Expense'
        verbose_name_plural = 'Expenses'

    def __str__(self) -> str:
        return f'Expense #{self.pk} for car {self.car}'

    def save(self, *args, **kwargs) -> None:
        self.base_currency_at_save = SYSTEM_BASE_CURRENCY
        if self.amount is not None:
            base_currency = SYSTEM_BASE_CURRENCY
            if self.currency == base_currency:
                self.exchange_rate = Decimal('1')
                self.amount_in_base_currency = self.amount
            else:
                if self.exchange_rate is None:
                    raise ValueError(
                        'Please provide an exchange rate when the expense'
                        ' currency differs from the base currency.'
                    )
                self.amount_in_base_currency = (
                    Decimal(self.amount) / Decimal(self.exchange_rate)
                ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        super().save(*args, **kwargs)


class ExpenseDocument(FileProcessingMixin, models.Model):
    FILE_FIELDS = {
        'file': FileProcessOptions(
            max_side=1600,
            quality=75,
        ),
    }

    expense = models.ForeignKey(
        Expense,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name='Expense',
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Description',
    )
    file = models.FileField(
        upload_to='expenses/%Y/%m/',
        verbose_name='File',
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    e.lstrip('.') for e in ALLOWED_UPLOAD_EXTENSIONS
                ]
            ),
        ],
    )

    class Meta:
        verbose_name = 'Expense document'
        verbose_name_plural = 'Expense documents'

    def __str__(self) -> str:
        return f'Document for expense #{self.expense_id}'
