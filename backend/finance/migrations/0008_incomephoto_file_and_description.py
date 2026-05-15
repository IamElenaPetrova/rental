import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0007_rename_attachment_doc_type_to_description'),
    ]

    operations = [
        migrations.RenameField(
            model_name='incomephoto',
            old_name='photo',
            new_name='file',
        ),
        migrations.AlterField(
            model_name='incomephoto',
            name='description',
            field=models.CharField(
                blank=True,
                max_length=255,
                verbose_name='Description',
            ),
        ),
        migrations.AlterField(
            model_name='incomephoto',
            name='file',
            field=models.FileField(
                upload_to='incomes/%Y/%m/',
                validators=[
                    django.core.validators.FileExtensionValidator(
                        allowed_extensions=[
                            'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp',
                            'pdf', 'doc', 'docx',
                        ],
                    ),
                ],
                verbose_name='File',
            ),
        ),
        migrations.AlterModelOptions(
            name='incomephoto',
            options={
                'verbose_name': 'Payment document',
                'verbose_name_plural': 'Payment documents',
            },
        ),
    ]
