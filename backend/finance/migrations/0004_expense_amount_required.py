# Generated manually

from decimal import Decimal

from django.db import migrations, models


def set_null_amounts_to_zero(apps, schema_editor):
    Expense = apps.get_model('finance', 'Expense')
    Expense.objects.filter(amount__isnull=True).update(amount=Decimal('0'))


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0003_initial'),
    ]

    operations = [
        migrations.RunPython(
            set_null_amounts_to_zero,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name='expense',
            name='amount',
            field=models.DecimalField(
                decimal_places=2,
                max_digits=10,
                verbose_name='Expense amount',
            ),
        ),
    ]
