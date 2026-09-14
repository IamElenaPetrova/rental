import django.core.validators
from django.db import migrations, models

import core.services


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='SiteSettings',
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
                    'hero_image',
                    models.FileField(
                        blank=True,
                        help_text=(
                            'Wide photo for the main page '
                            '(16:9 or 16:10 recommended).'
                        ),
                        null=True,
                        upload_to='site/hero/%Y/%m/',
                        validators=[
                            django.core.validators.FileExtensionValidator(
                                allowed_extensions=[
                                    e.lstrip('.')
                                    for e in core.services.IMAGE_EXTENSIONS
                                ]
                            ),
                        ],
                        verbose_name='Homepage hero image',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Site settings',
                'verbose_name_plural': 'Site settings',
            },
        ),
    ]
