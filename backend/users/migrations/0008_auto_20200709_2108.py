# Generated by Django 3.0.7 on 2020-07-09 18:08

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_auto_20200709_1445'),
    ]

    operations = [
        migrations.AlterField(
            model_name='investmentaccount',
            name='operations_sync_at',
            field=models.DateTimeField(default=datetime.datetime(1899, 12, 31, 21, 30, tzinfo=utc), verbose_name='Время последней синхронизации'),
        ),
    ]
