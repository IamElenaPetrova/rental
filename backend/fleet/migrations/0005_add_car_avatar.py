# Generated manually

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fleet', '0004_add_car_insurance_document'),
    ]

    operations = [
        migrations.AddField(
            model_name='car',
            name='avatar',
            field=models.FileField(
                blank=True,
                null=True,
                upload_to='cars/avatars/%Y/%m/',
                validators=[
                    django.core.validators.FileExtensionValidator(
                        allowed_extensions=[
                            'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp',
                        ]
                    )
                ],
                verbose_name='Avatar',
            ),
        ),
    ]
