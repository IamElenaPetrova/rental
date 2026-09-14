from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0002_house_publishable_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='house',
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
