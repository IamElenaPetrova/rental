from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fleet', '0006_add_car_inspection'),
    ]

    operations = [
        migrations.RenameField(
            model_name='carinsurancedocument',
            old_name='doc_type',
            new_name='description',
        ),
        migrations.AlterField(
            model_name='carinsurancedocument',
            name='description',
            field=models.TextField(blank=True, verbose_name='Description'),
        ),
    ]
