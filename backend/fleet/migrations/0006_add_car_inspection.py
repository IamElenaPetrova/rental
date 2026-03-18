# Generated manually

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fleet', '0005_add_car_avatar'),
    ]

    operations = [
        migrations.CreateModel(
            name='CarInspection',
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
                    'date',
                    models.DateField(verbose_name='Inspection date'),
                ),
                (
                    'place',
                    models.CharField(
                        blank=True,
                        max_length=255,
                        verbose_name='Place',
                    ),
                ),
                (
                    'comment',
                    models.TextField(
                        blank=True,
                        verbose_name='Comment',
                    ),
                ),
                (
                    'car',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='inspections',
                        to='fleet.car',
                        verbose_name='Car',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Car inspection',
                'verbose_name_plural': 'Car inspections',
                'ordering': ['-date'],
            },
        ),
    ]
