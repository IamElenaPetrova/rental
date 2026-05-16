import django.contrib.postgres.constraints
import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0009_alter_booking_status'),
        ('properties', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='HouseBooking',
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
                    'created_at',
                    models.DateTimeField(
                        auto_now_add=True,
                        verbose_name='Created at',
                    ),
                ),
                (
                    'updated_at',
                    models.DateTimeField(
                        auto_now=True,
                        verbose_name='Updated at',
                    ),
                ),
                (
                    'start_date',
                    models.DateField(verbose_name='Start date'),
                ),
                (
                    'end_date',
                    models.DateField(verbose_name='End date'),
                ),
                (
                    'rent_amount',
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=10,
                        verbose_name='Rent amount',
                    ),
                ),
                (
                    'currency',
                    models.CharField(
                        choices=[('USD', 'USD'), ('PESO', 'PESO')],
                        default='USD',
                        max_length=4,
                        verbose_name='Booking currency',
                    ),
                ),
                (
                    'status',
                    models.CharField(
                        choices=[
                            ('CONFIRMED', 'Confirmed'),
                            ('CANCELLED', 'Cancelled'),
                        ],
                        default='CONFIRMED',
                        max_length=20,
                        verbose_name='Status',
                    ),
                ),
                (
                    'comment',
                    models.TextField(
                        blank=True,
                        null=True,
                        verbose_name='Comment',
                    ),
                ),
                (
                    'contract',
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to='bookings/%Y/%m/',
                        validators=[
                            django.core.validators.FileExtensionValidator(
                                allowed_extensions=[
                                    'jpg', 'jpeg', 'png', 'gif', 'webp',
                                    'bmp', 'pdf', 'doc', 'docx',
                                ],
                            ),
                        ],
                        verbose_name='Contract',
                    ),
                ),
                (
                    'created_by',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='created_%(class)ss',
                        to=settings.AUTH_USER_MODEL,
                        verbose_name='Created by',
                    ),
                ),
                (
                    'renter',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='%(class)ss',
                        to='bookings.renter',
                        verbose_name='Renter',
                    ),
                ),
                (
                    'updated_by',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='updated_%(class)ss',
                        to=settings.AUTH_USER_MODEL,
                        verbose_name='Updated by',
                    ),
                ),
                (
                    'house',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='bookings',
                        to='properties.house',
                        verbose_name='House',
                    ),
                ),
            ],
            options={
                'verbose_name': 'House booking',
                'verbose_name_plural': 'House bookings',
            },
        ),
        migrations.AddConstraint(
            model_name='housebooking',
            constraint=django.contrib.postgres.constraints.ExclusionConstraint(
                name='house_booking_no_overlaps',
                expressions=[
                    ('house', '='),
                    (
                        models.Func(
                            models.F('start_date'),
                            models.F('end_date'),
                            function='daterange',
                            template="%(function)s(%(expressions)s, '[]')",
                        ),
                        '&&',
                    ),
                ],
                condition=models.Q(('status', 'CANCELLED'), _negated=True),
            ),
        ),
    ]
