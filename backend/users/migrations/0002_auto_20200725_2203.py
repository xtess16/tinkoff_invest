# Generated by Django 3.0.8 on 2020-07-25 22:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coowner',
            name='default_share',
            field=models.DecimalField(decimal_places=6, default=0, max_digits=7, verbose_name='Доля по умолчанию'),
        ),
    ]
