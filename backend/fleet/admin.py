from django.contrib import admin
from finance.models import Expense
from .models import Car, CarPhoto, InsuranceCompany, CarInsurance


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


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('name', 'plate_number', 'is_active', 'owners_display', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'plate_number')
    filter_vertical = ('owners',)
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    inlines = (CarInsuranceInline, CarPhotoInline, ExpenseInline,)
    fieldsets = (
        (None, {
            'fields': ('name', 'plate_number', 'owners', 'is_active'),
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('owners')

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
