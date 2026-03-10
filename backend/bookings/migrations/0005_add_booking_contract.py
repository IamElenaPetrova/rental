# Generated manually

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0004_add_renter_document'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='contract',
            field=models.FileField(
                blank=True,
                null=True,
                upload_to='bookings/%Y/%m/',
                validators=[
                    django.core.validators.FileExtensionValidator(
                        allowed_extensions=[
                            'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp',
                            'pdf', 'doc', 'docx',
                        ]
                    ),
                ],
                verbose_name='Contract',
            ),
        ),
    ]
