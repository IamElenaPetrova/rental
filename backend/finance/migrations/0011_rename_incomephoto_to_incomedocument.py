import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0010_rename_expensephoto_to_expensedocument'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='IncomePhoto',
            new_name='IncomeDocument',
        ),
        migrations.AlterField(
            model_name='incomedocument',
            name='income',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='documents',
                to='finance.income',
                verbose_name='Payment',
            ),
        ),
    ]
