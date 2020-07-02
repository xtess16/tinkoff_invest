# Generated by Django 3.0.7 on 2020-07-01 22:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_auto_20200630_1904'),
    ]

    operations = [
        migrations.AddField(
            model_name='investor',
            name='default_investment_account',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='users.InvestmentAccount', verbose_name='Инвестиционный счет по умолчанию'),
        ),
    ]
