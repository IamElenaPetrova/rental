from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fleet', '0008_car_gallery_and_documents'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carinsurancedocument',
            name='description',
            field=models.CharField(
                blank=True,
                max_length=255,
                verbose_name='Description',
            ),
        ),
    ]
