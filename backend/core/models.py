from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

User = get_user_model()


class BaseModel(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created at',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated at',
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='created_%(class)ss',
        verbose_name='Created by',
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='updated_%(class)ss',
        verbose_name='Updated by',
    )

    class Meta:
        abstract = True
        ordering = ('-created_at',)


class PublishableMixin(models.Model):
    """Fields for the public catalog (site / future API).

    i18n: when adding Spanish, add *_es fields and branch in get_*()
    by get_language().
    """

    is_published = models.BooleanField(
        default=False,
        verbose_name='Published on site',
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        null=True,
        verbose_name='URL slug',
        help_text='Used in the URL, e.g. toyota-rav4-2022',
    )
    public_title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Public title',
        help_text='Heading on the site. Falls back to internal name if empty.',
    )
    public_description = models.TextField(
        blank=True,
        verbose_name='Public description',
    )
    public_location = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Public location',
        help_text=(
            'Area for guests, e.g. Bávaro, Punta Cana. Not the full address.'
        ),
    )
    daily_rate_from = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Daily rate from',
    )
    meta_title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='SEO title',
        help_text=(
            'Browser tab / search results. Falls back to public title or name.'
        ),
    )
    meta_description = models.CharField(
        max_length=512,
        blank=True,
        verbose_name='SEO description',
        help_text='Search snippet. Falls back to public description if empty.',
    )

    class Meta:
        abstract = True

    def get_public_title(self) -> str:
        return (self.public_title or '').strip() or self.name

    def get_meta_title(self) -> str:
        return (self.meta_title or '').strip() or self.get_public_title()

    def get_meta_description(self) -> str:
        if (self.meta_description or '').strip():
            return self.meta_description.strip()
        desc = (self.public_description or '').strip()
        return desc[:512] if desc else ''

    def clean(self):
        super().clean()
        if self.is_published and not (self.slug or '').strip():
            raise ValidationError(
                {'slug': 'Slug is required when the listing is published.'},
            )
