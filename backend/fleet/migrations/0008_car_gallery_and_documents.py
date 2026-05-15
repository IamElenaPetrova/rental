import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fleet', '0007_rename_insurance_doc_type_to_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='carphoto',
            name='sort_order',
            field=models.PositiveSmallIntegerField(
                default=0,
                help_text='Lower numbers appear first in the gallery.',
                verbose_name='Sort order',
            ),
        ),
        migrations.AddField(
            model_name='carphoto',
            name='description',
            field=models.CharField(
                blank=True,
                max_length=255,
                verbose_name='Description',
            ),
        ),
        migrations.AlterModelOptions(
            name='carphoto',
            options={
                'ordering': ['sort_order', 'id'],
                'verbose_name': 'Car gallery photo',
                'verbose_name_plural': 'Car gallery photos',
            },
        ),
        migrations.AlterField(
            model_name='carphoto',
            name='photo',
            field=models.FileField(
                upload_to='cars/gallery/%Y/%m/',
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
        migrations.CreateModel(
            name='CarDocument',
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
                        upload_to='cars/documents/%Y/%m/',
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
                    'car',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='documents',
                        to='fleet.car',
                        verbose_name='Car',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Car document',
                'verbose_name_plural': 'Car documents',
                'ordering': ['-id'],
            },
        ),
    ]
