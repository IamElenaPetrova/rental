from django.contrib import admin
from django.utils.html import format_html

from finance.models import HouseExpense

from .models import House, HouseDocument, HousePhoto


class HouseExpenseInline(admin.TabularInline):
    model = HouseExpense
    fk_name = 'house'
    extra = 0
    fields = (
        'description_short',
        'date',
        'payed_by',
        'amount',
        'currency',
        'amount_in_base_currency',
    )
    readonly_fields = ('description_short', 'amount_in_base_currency')
    autocomplete_fields = ('payed_by',)
    show_change_link = True
    ordering = ('-date',)
    verbose_name = 'Expense'
    verbose_name_plural = 'House expenses'

    def description_short(self, obj):
        if obj is None:
            return ''
        text = obj.description or ''
        return text[:60] + ('…' if len(text) > 60 else '')

    description_short.short_description = 'Description'


class HousePhotoInline(admin.TabularInline):
    model = HousePhoto
    fk_name = 'house'
    extra = 0
    fields = ('sort_order', 'description', 'photo')
    ordering = ('sort_order', 'id')
    verbose_name = 'Gallery photo'
    verbose_name_plural = 'Gallery'


class HouseDocumentInline(admin.TabularInline):
    model = HouseDocument
    fk_name = 'house'
    extra = 0
    fields = ('description', 'file')
    verbose_name = 'House document'
    verbose_name_plural = 'Documents'


@admin.register(House)
class HouseAdmin(admin.ModelAdmin):
    list_display = (
        'avatar_thumb',
        'name',
        'address',
        'is_active',
        'is_published',
        'owners_display',
        'created_at',
    )
    list_filter = ('is_active', 'is_published')
    search_fields = ('name', 'address', 'comment', 'slug', 'public_title')
    prepopulated_fields = {'slug': ('public_title', 'name')}
    filter_vertical = ('owners',)
    readonly_fields = (
        'created_at',
        'updated_at',
        'created_by',
        'updated_by',
    )
    inlines = (HousePhotoInline, HouseDocumentInline, HouseExpenseInline)
    fieldsets = (
        (None, {
            'fields': (
                'avatar',
                'name',
                'address',
                'owners',
                'is_active',
                'comment',
            ),
        }),
        ('Public site', {
            'fields': (
                'is_published',
                'slug',
                'public_title',
                'public_description',
                'public_location',
                'daily_rate_from',
                'meta_title',
                'meta_description',
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

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('owners')

    def avatar_thumb(self, obj):
        if not obj.avatar:
            return '—'
        try:
            url = obj.avatar.url
        except Exception:
            return '—'
        return format_html(
            '<img src="{}" '
            'style="height:40px;width:40px;object-fit:cover;" />',
            url,
        )

    avatar_thumb.short_description = 'Avatar'

    def owners_display(self, obj):
        return ', '.join(str(u) for u in obj.owners.all()) or '—'

    owners_display.short_description = 'Owners'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
