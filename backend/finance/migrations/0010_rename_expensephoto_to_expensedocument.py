import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0009_expensephoto_file_and_description'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ExpensePhoto',
            new_name='ExpenseDocument',
        ),
        migrations.AlterField(
            model_name='expensedocument',
            name='expense',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='documents',
                to='finance.expense',
                verbose_name='Expense',
            ),
        ),
    ]
