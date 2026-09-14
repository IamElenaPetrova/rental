from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fleet', '0010_car_publishable_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='car',
            name='contact_phone',
            field=models.CharField(
                blank=True,
                help_text=(
                    'International format, digits only, e.g. 18095551234 '
                    '(no + or spaces).'
                ),
                max_length=32,
                verbose_name='WhatsApp phone',
            ),
        ),
    ]
