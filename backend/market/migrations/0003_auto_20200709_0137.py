# Generated by Django 3.0.7 on 2020-07-08 22:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0002_remove_deal_is_closed'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='operation',
            constraint=models.UniqueConstraint(fields=('type', 'date', 'investment_account'), name='unique operation'),
        ),
    ]
