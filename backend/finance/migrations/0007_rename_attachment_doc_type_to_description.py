from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0006_alter_income_booking'),
    ]

    operations = [
        migrations.RenameField(
            model_name='incomephoto',
            old_name='doc_type',
            new_name='description',
        ),
        migrations.AlterField(
            model_name='incomephoto',
            name='description',
            field=models.TextField(blank=True, verbose_name='Description'),
        ),
        migrations.RenameField(
            model_name='expensephoto',
            old_name='doc_type',
            new_name='description',
        ),
        migrations.AlterField(
            model_name='expensephoto',
            name='description',
            field=models.TextField(blank=True, verbose_name='Description'),
        ),
    ]
