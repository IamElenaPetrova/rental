import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0008_incomephoto_file_and_description'),
    ]

    operations = [
        migrations.RenameField(
            model_name='expensephoto',
            old_name='photo',
            new_name='file',
        ),
        migrations.AlterField(
            model_name='expensephoto',
            name='description',
            field=models.CharField(
                blank=True,
                max_length=255,
                verbose_name='Description',
            ),
        ),
        migrations.AlterField(
            model_name='expensephoto',
            name='file',
            field=models.FileField(
                upload_to='expenses/%Y/%m/',
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
            name='expensephoto',
            options={
                'verbose_name': 'Expense document',
                'verbose_name_plural': 'Expense documents',
            },
        ),
    ]
