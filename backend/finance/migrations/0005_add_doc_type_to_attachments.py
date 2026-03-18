# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0004_expense_amount_required'),
    ]

    operations = [
        migrations.AddField(
            model_name='incomephoto',
            name='doc_type',
            field=models.CharField(
                blank=True,
                max_length=255,
                verbose_name='Document type',
            ),
        ),
        migrations.AddField(
            model_name='expensephoto',
            name='doc_type',
            field=models.CharField(
                blank=True,
                max_length=255,
                verbose_name='Document type',
            ),
        ),
    ]
