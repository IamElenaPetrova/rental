import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='House',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'created_at',
                    models.DateTimeField(
                        auto_now_add=True,
                        verbose_name='Created at',
                    ),
                ),
                (
                    'updated_at',
                    models.DateTimeField(
                        auto_now=True,
                        verbose_name='Updated at',
                    ),
                ),
                (
                    'name',
                    models.CharField(max_length=255, verbose_name='Name'),
                ),
                (
                    'address',
                    models.CharField(max_length=512, verbose_name='Address'),
                ),
                (
                    'is_active',
                    models.BooleanField(default=True, verbose_name='Active'),
                ),
                (
                    'comment',
                    models.TextField(blank=True, verbose_name='Comment'),
                ),
                (
                    'avatar',
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to='houses/avatars/%Y/%m/',
                        validators=[
                            django.core.validators.FileExtensionValidator(
                                allowed_extensions=[
                                    'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp',
                                ],
                            ),
                        ],
                        verbose_name='Avatar',
                    ),
                ),
                (
                    'created_by',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='created_%(class)ss',
                        to=settings.AUTH_USER_MODEL,
                        verbose_name='Created by',
                    ),
                ),
                (
                    'updated_by',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='updated_%(class)ss',
                        to=settings.AUTH_USER_MODEL,
                        verbose_name='Updated by',
                    ),
                ),
                (
                    'owners',
                    models.ManyToManyField(
                        related_name='houses',
                        to=settings.AUTH_USER_MODEL,
                        verbose_name='Owners',
                    ),
                ),
            ],
            options={
                'verbose_name': 'House',
                'verbose_name_plural': 'Houses',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='HousePhoto',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'sort_order',
                    models.PositiveSmallIntegerField(
                        default=0,
                        help_text=(
                            'Lower numbers appear first in the gallery.'
                        ),
                        verbose_name='Sort order',
                    ),
                ),
                (
                    'description',
                    models.CharField(
                        blank=True,
                        max_length=255,
                        verbose_name='Description',
                    ),
                ),
                (
                    'photo',
                    models.FileField(
                        upload_to='houses/gallery/%Y/%m/',
                        validators=[
                            django.core.validators.FileExtensionValidator(
                                allowed_extensions=[
                                    'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp',
                                ],
                            ),
                        ],
                        verbose_name='Photo',
                    ),
                ),
                (
                    'house',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='photos',
                        to='properties.house',
                        verbose_name='House',
                    ),
                ),
            ],
            options={
                'verbose_name': 'House gallery photo',
                'verbose_name_plural': 'House gallery photos',
                'ordering': ['sort_order', 'id'],
            },
        ),
        migrations.CreateModel(
            name='HouseDocument',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'description',
                    models.CharField(
                        blank=True,
                        max_length=255,
                        verbose_name='Description',
                    ),
                ),
                (
                    'file',
                    models.FileField(
                        upload_to='houses/documents/%Y/%m/',
                        validators=[
                            django.core.validators.FileExtensionValidator(
                                allowed_extensions=[
                                    'jpg', 'jpeg', 'png', 'gif', 'webp',
                                    'bmp', 'pdf', 'doc', 'docx',
                                ],
                            ),
                        ],
                        verbose_name='File',
                    ),
                ),
                (
                    'house',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='documents',
                        to='properties.house',
                        verbose_name='House',
                    ),
                ),
            ],
            options={
                'verbose_name': 'House document',
                'verbose_name_plural': 'House documents',
                'ordering': ['-id'],
            },
        ),
    ]
