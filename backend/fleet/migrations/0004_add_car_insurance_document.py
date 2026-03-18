# Generated manually

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fleet', '0003_add_car_photo'),
    ]

    operations = [
        migrations.CreateModel(
            name='CarInsuranceDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('doc_type', models.CharField(blank=True, max_length=255, verbose_name='Document type')),
                (
                    'file',
                    models.FileField(
                        upload_to='insurances/%Y/%m/',
                        validators=[
                            django.core.validators.FileExtensionValidator(
                                allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'pdf', 'doc', 'docx']
                            )
                        ],
                        verbose_name='Attachment',
                    ),
                ),
                (
                    'insurance',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='documents',
                        to='fleet.carinsurance',
                        verbose_name='Car insurance',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Insurance attachment',
                'verbose_name_plural': 'Insurance attachments',
            },
        ),
    ]

