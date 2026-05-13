from datetime import timedelta
from calendar import monthrange

from django.contrib import admin
from django.db.models import Max
from django.utils import timezone
from django.utils.html import format_html
from finance.models import Expense
from .models import (
    Car,
    CarPhoto,
    InsuranceCompany,
    CarInsurance,
    CarInsuranceDocument,
    CarInspection,
)


class ExpenseInline(admin.TabularInline):
    model = Expense
    fk_name = 'car'
    extra = 0
    fields = ('description_short', 'date', 'payed_by', 'amount', 'currency', 'amount_in_base_currency')
    readonly_fields = ('description_short', 'amount_in_base_currency',)
    autocomplete_fields = ('payed_by',)
    show_change_link = True
    ordering = ('-date',)
    verbose_name = 'Expense'
    verbose_name_plural = 'Car expenses'

    def description_short(self, obj):
        if obj is None:
            return ''
        text = obj.description or ''
        return text[:60] + ('…' if len(text) > 60 else '')

    description_short.short_description = 'Description'


class CarInsuranceInline(admin.TabularInline):
    model = CarInsurance
    fk_name = 'car'
    extra = 0
    fields = ('insurer', 'policy_number', 'start_date', 'end_date')
    autocomplete_fields = ('insurer',)
    show_change_link = True


class CarPhotoInline(admin.TabularInline):
    model = CarPhoto
    fk_name = 'car'
    extra = 0
    fields = ('photo',)
    verbose_name = 'Attachment'
    verbose_name_plural = 'Attachments'


class CarInsuranceDocumentInline(admin.TabularInline):
    model = CarInsuranceDocument
    fk_name = 'insurance'
    extra = 0
    fields = ('description', 'file')
    verbose_name = 'Insurance attachment'
    verbose_name_plural = 'Insurance attachments'


class CarInspectionInline(admin.TabularInline):
    model = CarInspection
    fk_name = 'car'
    extra = 0
    fields = ('date', 'place', 'comment')
    ordering = ('-date',)
    verbose_name = 'Inspection'
    verbose_name_plural = 'Inspections'


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = (
        'avatar_thumb',
        'name',
        'plate_number',
        'is_active',
        'last_inspection_date_display',
        'last_insurance_end_date_display',
        'owners_display',
        'created_at',
    )
    list_filter = ('is_active',)
    search_fields = ('name', 'plate_number')
    filter_vertical = ('owners',)
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    inlines = (
        CarInsuranceInline,
        CarPhotoInline,
        CarInspectionInline,
        ExpenseInline,
    )
    fieldsets = (
        (None, {
            'fields': ('avatar', 'name', 'plate_number', 'owners', 'is_active'),
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',),
        }),
    )

    def avatar_thumb(self, obj):
        if not obj.avatar:
            return '—'
        try:
            url = obj.avatar.url
        except Exception:
            return '—'
        return format_html(
            '<img src="{}" style="height:40px;width:40px;object-fit:cover;" />',
            url,
        )

    avatar_thumb.short_description = 'Avatar'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('owners').annotate(
            last_inspection_date=Max('inspections__date'),
            last_insurance_end_date=Max('insurances__end_date'),
        )

    def last_inspection_date_display(self, obj):
        date = getattr(obj, 'last_inspection_date', None)
        if not date:
            return '—'

        today = timezone.localdate()

        def add_months(d, months):
            # Calendar-safe month shifting (e.g. 31st -> last day of target month)
            month = d.month - 1 + months
            year = d.year + month // 12
            month = month % 12 + 1
            day = min(d.day, monthrange(year, month)[1])
            return d.replace(year=year, month=month, day=day)

        limit_6 = add_months(today, -6)
        limit_5 = add_months(today, -5)

        text = date.strftime('%d %b %y')
        if date <= limit_6:
            return format_html(
                '<span style="color:{}; font-weight:600;">{}</span>',
                'red',
                text,
            )
        if date < limit_5:
            return format_html(
                '<span style="color:{}; font-weight:600;">{}</span>',
                '#d97706',
                text,
            )
        return text

    last_inspection_date_display.short_description = 'Last inspection'
    last_inspection_date_display.admin_order_field = 'last_inspection_date'

    def last_insurance_end_date_display(self, obj):
        date = getattr(obj, 'last_insurance_end_date', None)
        if not date:
            return '—'
        today = timezone.localdate()
        limit = today + timedelta(days=30)
        if date < today:
            color = 'red'
        elif date <= limit:
            color = '#d97706'
        else:
            color = 'inherit'
        text = date.strftime('%d %b %y')
        if color == 'inherit':
            return text
        return format_html(
            '<span style="color:{}; font-weight:600;">{}</span>',
            color,
            text,
        )

    last_insurance_end_date_display.short_description = 'Insurance end'
    last_insurance_end_date_display.admin_order_field = 'last_insurance_end_date'

    def owners_display(self, obj):
        return ', '.join(str(u) for u in obj.owners.all()) or '—'

    owners_display.short_description = 'Owners'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(InsuranceCompany)
class InsuranceCompanyAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(CarInsurance)
class CarInsuranceAdmin(admin.ModelAdmin):
    list_display = ('car', 'insurer', 'policy_number', 'start_date', 'end_date')
    list_filter = ('insurer',)
    search_fields = ('policy_number', 'car__name', 'car__plate_number')
    autocomplete_fields = ('car', 'insurer')
    date_hierarchy = 'start_date'
    inlines = (CarInsuranceDocumentInline,)


@admin.register(CarInspection)
class CarInspectionAdmin(admin.ModelAdmin):
    list_display = ('car', 'date', 'place', 'comment_short')
    list_filter = ('car',)
    search_fields = ('place', 'comment', 'car__name', 'car__plate_number')
    autocomplete_fields = ('car',)
    date_hierarchy = 'date'
    ordering = ('-date',)

    def comment_short(self, obj):
        if not obj.comment:
            return '—'
        return obj.comment[:50] + ('…' if len(obj.comment) > 50 else '')

    comment_short.short_description = 'Comment'
