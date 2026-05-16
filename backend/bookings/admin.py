from decimal import Decimal

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import Sum, F, Q, Value, DecimalField
from django.db.models.functions import Coalesce
from django.urls import reverse
from django.utils.html import format_html

from finance.models import Income
from .models import Booking, HouseBooking, Renter


class PaymentStatusFilter(admin.SimpleListFilter):
    title = 'payment status'
    parameter_name = 'payment_status'

    def lookups(self, request, model_admin):
        return (
            ('paid', 'Paid'),
            ('unpaid', 'Unpaid'),
            ('partially_paid', 'Partially paid'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'paid':
            return queryset.annotate(
                _paid=Coalesce(
                    F('_total_paid'),
                    Value(Decimal('0'), output_field=DecimalField()),
                )
            ).filter(_paid__gte=F('rent_amount'))
        if self.value() == 'unpaid':
            return queryset.filter(
                Q(_total_paid__isnull=True) | Q(_total_paid=0)
            )
        if self.value() == 'partially_paid':
            return queryset.filter(
                _total_paid__isnull=False,
                _total_paid__gt=0,
                rent_amount__gt=F('_total_paid'),
            )
        return queryset


class IncomeInline(admin.TabularInline):
    model = Income
    fk_name = 'booking'
    extra = 0
    fields = (
        'amount',
        'currency',
        'exchange_rate',
        'amount_in_booking_currency',
        'received_by',
        'documents_link',
    )
    readonly_fields = (
        'amount_currency_display',
        'amount_in_booking_currency',
        'documents_link',
    )
    autocomplete_fields = ('received_by',)
    show_change_link = True

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('documents')

    def documents_link(self, obj):
        if obj is None or not obj.pk:
            return '—'
        count = obj.documents.count()
        url = reverse('admin:finance_income_change', args=(obj.pk,))
        if count == 0:
            return format_html('<a href="{}">+</a>', url)
        return format_html('<a href="{}">{}</a>', url, count)

    documents_link.short_description = 'Docs'

    def amount_currency_display(self, obj):
        if obj is None or not obj.pk:
            return '—'
        return f'{obj.amount} {obj.currency}'

    amount_currency_display.short_description = 'Amount (currency)'


@admin.register(Renter)
class RenterAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'phone')
    search_fields = ('first_name', 'last_name', 'phone')
    fields = ('first_name', 'last_name', 'phone', 'comment', 'document')


@admin.register(Booking)
class CarBookingAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'car',
        'renter',
        'start_date',
        'end_date',
        'start_mileage',
        'end_mileage',
        'rent_amount_display',
        'display_total_paid',
    )

    def rent_amount_display(self, obj):
        if obj is None:
            return '—'
        return f'{obj.rent_amount} {obj.currency}'

    rent_amount_display.short_description = 'Rent amount'
    list_filter = (PaymentStatusFilter, 'currency', 'car',)
    search_fields = (
        'renter__first_name',
        'renter__last_name',
        'renter__phone',
    )
    inlines = (IncomeInline,)
    autocomplete_fields = ('renter',)
    readonly_fields = (
        'created_at',
        'updated_at',
        'created_by',
        'updated_by',
        'total_paid_display',
    )
    date_hierarchy = 'start_date'
    fieldsets = (
        (None, {
            'fields': (
                'car',
                'renter',
                'start_date',
                'start_mileage',
                'end_date',
                'end_mileage',
                'rent_amount',
                'total_paid_display',
                'currency',
                'status',
                'comment',
                'contract',
            ),
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',),
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            _total_paid=Sum('incomes__amount_in_booking_currency')
        )

    def display_total_paid(self, obj):
        total = getattr(obj, '_total_paid', None)
        if total is None:
            return '0'
        return f'{total} {obj.currency}'

    display_total_paid.short_description = 'Paid'

    def total_paid_display(self, obj):
        if obj is None:
            return ''
        result = obj.incomes.aggregate(
            total=Sum('amount_in_booking_currency')
        )
        total = result.get('total')
        if total is None:
            return '0'
        return f'{total} {obj.currency}'

    total_paid_display.short_description = 'Paid'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        try:
            with transaction.atomic():
                super().save_model(request, obj, form, change)
        except IntegrityError as exc:
            if 'booking_no_overlaps_per_car' in str(exc):
                raise ValidationError(
                    {'start_date': 'This booking overlaps with another booking for this car.'}
                )
            raise

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, Income):
                if not instance.pk:
                    instance.created_by = request.user
                instance.updated_by = request.user
                instance.save()
        formset.save_m2m()


@admin.register(HouseBooking)
class HouseBookingAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'house',
        'renter',
        'start_date',
        'end_date',
        'rent_amount_display',
        'status',
    )

    def rent_amount_display(self, obj):
        if obj is None:
            return '—'
        return f'{obj.rent_amount} {obj.currency}'

    rent_amount_display.short_description = 'Rent amount'

    list_filter = ('status', 'currency', 'house')
    search_fields = (
        'renter__first_name',
        'renter__last_name',
        'renter__phone',
        'house__name',
        'house__address',
    )
    autocomplete_fields = ('renter', 'house')
    readonly_fields = (
        'created_at',
        'updated_at',
        'created_by',
        'updated_by',
    )
    date_hierarchy = 'start_date'
    fieldsets = (
        (None, {
            'fields': (
                'house',
                'renter',
                'start_date',
                'end_date',
                'rent_amount',
                'currency',
                'status',
                'comment',
                'contract',
            ),
        }),
        ('Audit', {
            'fields': (
                'created_at',
                'updated_at',
                'created_by',
                'updated_by',
            ),
            'classes': ('collapse',),
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        try:
            with transaction.atomic():
                super().save_model(request, obj, form, change)
        except IntegrityError as exc:
            if 'house_booking_no_overlaps' in str(exc):
                raise ValidationError({
                    'start_date': (
                        'This booking overlaps with another booking '
                        'for this house.'
                    ),
                })
            raise
