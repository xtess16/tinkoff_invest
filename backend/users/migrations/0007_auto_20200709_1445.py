# Generated by Django 3.0.7 on 2020-07-09 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20200709_0320'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coowner',
            name='share',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=8, verbose_name='Доля'),
        ),
    ]
