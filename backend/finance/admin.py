from django.contrib import admin

from core.constants import SYSTEM_BASE_CURRENCY
from .models import (
    Expense,
    ExpenseDocument,
    HouseExpense,
    HouseExpenseDocument,
    HouseIncome,
    HouseIncomeDocument,
    Income,
    IncomeDocument,
)


class IncomeDocumentInline(admin.TabularInline):
    model = IncomeDocument
    extra = 0
    fields = ('description', 'file')
    verbose_name = 'Payment document'
    verbose_name_plural = 'Payment documents'


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'booking',
        'amount_currency_display',
        'booking_currency_display',
        'received_by_display',
    )

    def received_by_display(self, obj):
        return obj.received_by if obj else '—'

    received_by_display.short_description = 'Recipient'

    def amount_currency_display(self, obj):
        if obj is None:
            return '—'
        return f'{obj.amount} {obj.currency}'

    amount_currency_display.short_description = 'Payment'

    def booking_currency_display(self, obj):
        if obj is None or obj.amount_in_booking_currency is None:
            return '—'
        return obj.amount_in_booking_currency

    booking_currency_display.short_description = 'In booking curr.'

    list_filter = ('received_by', 'booking', 'currency')
    search_fields = ('booking__id',)
    readonly_fields = (
        'amount_in_booking_currency',
        'created_at',
        'updated_at',
        'created_by',
        'updated_by',
    )
    inlines = (IncomeDocumentInline,)
    date_hierarchy = 'received_date'
    fieldsets = (
        (None, {
            'fields': (
                'booking',
                'received_date',
                'amount',
                'currency',
                'exchange_rate',
                'amount_in_booking_currency',
                'received_by',
            ),
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',),
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


class ExpenseDocumentInline(admin.TabularInline):
    model = ExpenseDocument
    extra = 0
    fields = ('description', 'file')
    verbose_name = 'Expense document'
    verbose_name_plural = 'Expense documents'


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'car',
        'description',
        'date',
        'payed_by',
        'amount_display',
    )
    list_filter = ('car', 'payed_by', 'date', 'currency')
    search_fields = ('description',)
    readonly_fields = (
        'amount_in_base_currency',
        'base_currency_at_save',
        'created_at',
        'updated_at',
        'created_by',
        'updated_by',
    )
    date_hierarchy = 'date'
    inlines = (ExpenseDocumentInline,)
    fieldsets = (
        (None, {
            'fields': (
                'car',
                'description',
                'date',
                'payed_by',
                'amount',
                'currency',
                'exchange_rate',
                'amount_in_base_currency',
                'base_currency_at_save',
            ),
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',),
        }),
    )

    def amount_display(self, obj):
        if obj is None or obj.amount_in_base_currency is None:
            return '—'
        return f'{obj.amount_in_base_currency:.2f} {SYSTEM_BASE_CURRENCY}'

    amount_display.short_description = 'Amount (base currency)'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


class HouseIncomeDocumentInline(admin.TabularInline):
    model = HouseIncomeDocument
    extra = 0
    fields = ('description', 'file')
    verbose_name = 'Payment document'
    verbose_name_plural = 'Payment documents'


@admin.register(HouseIncome)
class HouseIncomeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'house_booking',
        'amount_currency_display',
        'booking_currency_display',
        'received_by_display',
    )

    def received_by_display(self, obj):
        return obj.received_by if obj else '—'

    received_by_display.short_description = 'Recipient'

    def amount_currency_display(self, obj):
        if obj is None:
            return '—'
        return f'{obj.amount} {obj.currency}'

    amount_currency_display.short_description = 'Payment'

    def booking_currency_display(self, obj):
        if obj is None or obj.amount_in_booking_currency is None:
            return '—'
        return obj.amount_in_booking_currency

    booking_currency_display.short_description = 'In booking curr.'

    list_filter = ('received_by', 'house_booking', 'currency')
    search_fields = ('house_booking__id', 'house_booking__house__name')
    readonly_fields = (
        'amount_in_booking_currency',
        'created_at',
        'updated_at',
        'created_by',
        'updated_by',
    )
    autocomplete_fields = ('house_booking', 'received_by')
    inlines = (HouseIncomeDocumentInline,)
    date_hierarchy = 'received_date'
    fieldsets = (
        (None, {
            'fields': (
                'house_booking',
                'received_date',
                'amount',
                'currency',
                'exchange_rate',
                'amount_in_booking_currency',
                'received_by',
            ),
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',),
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


class HouseExpenseDocumentInline(admin.TabularInline):
    model = HouseExpenseDocument
    extra = 0
    fields = ('description', 'file')
    verbose_name = 'Expense document'
    verbose_name_plural = 'Expense documents'


@admin.register(HouseExpense)
class HouseExpenseAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'house',
        'description',
        'date',
        'payed_by',
        'amount_display',
    )
    list_filter = ('house', 'payed_by', 'date', 'currency')
    search_fields = ('description', 'house__name', 'house__address')
    readonly_fields = (
        'amount_in_base_currency',
        'base_currency_at_save',
        'created_at',
        'updated_at',
        'created_by',
        'updated_by',
    )
    autocomplete_fields = ('house', 'payed_by')
    date_hierarchy = 'date'
    inlines = (HouseExpenseDocumentInline,)
    fieldsets = (
        (None, {
            'fields': (
                'house',
                'description',
                'date',
                'payed_by',
                'amount',
                'currency',
                'exchange_rate',
                'amount_in_base_currency',
                'base_currency_at_save',
            ),
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',),
        }),
    )

    def amount_display(self, obj):
        if obj is None or obj.amount_in_base_currency is None:
            return '—'
        return f'{obj.amount_in_base_currency:.2f} {SYSTEM_BASE_CURRENCY}'

    amount_display.short_description = 'Amount (base currency)'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
