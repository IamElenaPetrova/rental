# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0005_add_booking_contract'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='start_mileage',
            field=models.PositiveIntegerField(
                blank=True,
                null=True,
                verbose_name='Start mileage',
            ),
        ),
        migrations.AddField(
            model_name='booking',
            name='end_mileage',
            field=models.PositiveIntegerField(
                blank=True,
                null=True,
                verbose_name='End mileage',
            ),
        ),
    ]

