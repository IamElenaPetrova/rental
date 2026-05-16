from django.contrib import admin
from django.utils.html import format_html

from .models import House, HouseDocument, HousePhoto


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
        'owners_display',
        'created_at',
    )
    list_filter = ('is_active',)
    search_fields = ('name', 'address', 'comment')
    filter_vertical = ('owners',)
    readonly_fields = (
        'created_at',
        'updated_at',
        'created_by',
        'updated_by',
    )
    inlines = (HousePhotoInline, HouseDocumentInline)
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
