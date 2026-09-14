from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='house',
            name='is_published',
            field=models.BooleanField(
                default=False,
                verbose_name='Published on site',
            ),
        ),
        migrations.AddField(
            model_name='house',
            name='slug',
            field=models.SlugField(
                blank=True,
                null=True,
                max_length=255,
                unique=True,
                verbose_name='URL slug',
                help_text='Used in the URL, e.g. villa-bavaro',
            ),
        ),
        migrations.AddField(
            model_name='house',
            name='public_title',
            field=models.CharField(
                blank=True,
                max_length=255,
                verbose_name='Public title',
                help_text=(
                    'Heading on the site. Falls back to internal name if empty.'
                ),
            ),
        ),
        migrations.AddField(
            model_name='house',
            name='public_description',
            field=models.TextField(
                blank=True,
                verbose_name='Public description',
            ),
        ),
        migrations.AddField(
            model_name='house',
            name='public_location',
            field=models.CharField(
                blank=True,
                max_length=255,
                verbose_name='Public location',
                help_text=(
                    'Area for guests, e.g. Bávaro, Punta Cana. '
                    'Not the full address.'
                ),
            ),
        ),
        migrations.AddField(
            model_name='house',
            name='daily_rate_from',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=10,
                null=True,
                verbose_name='Daily rate from',
            ),
        ),
        migrations.AddField(
            model_name='house',
            name='meta_title',
            field=models.CharField(
                blank=True,
                max_length=255,
                verbose_name='SEO title',
                help_text=(
                    'Browser tab / search results. '
                    'Falls back to public title or name.'
                ),
            ),
        ),
        migrations.AddField(
            model_name='house',
            name='meta_description',
            field=models.CharField(
                blank=True,
                max_length=512,
                verbose_name='SEO description',
                help_text=(
                    'Search snippet. Falls back to public description if empty.'
                ),
            ),
        ),
    ]
