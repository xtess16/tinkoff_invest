# Generated by Django 3.0.8 on 2020-08-15 00:28

import datetime
from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='Investor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='CoOwner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('capital', models.DecimalField(decimal_places=4, default=0, max_digits=20, verbose_name='Капитал')),
                ('default_share', models.DecimalField(decimal_places=8, default=0, max_digits=9, verbose_name='Доля по умолчанию')),
            ],
            options={
                'verbose_name': 'Совладелец',
                'verbose_name_plural': 'Совладельцы',
            },
        ),
        migrations.CreateModel(
            name='CurrencyAsset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.DecimalField(decimal_places=4, default=0, max_digits=20, verbose_name='Количество')),
            ],
            options={
                'verbose_name': 'Валютный актив',
                'verbose_name_plural': 'Валютные активы',
                'ordering': ('currency',),
            },
        ),
        migrations.CreateModel(
            name='InvestorGroup',
            fields=[
            ],
            options={
                'verbose_name': 'Группа пользователей',
                'verbose_name_plural': 'Группы пользователей',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('auth.group',),
            managers=[
                ('objects', django.contrib.auth.models.GroupManager()),
            ],
        ),
        migrations.CreateModel(
            name='InvestmentAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, verbose_name='Название счета')),
                ('token', models.CharField(max_length=128, verbose_name='Токен для торговли')),
                ('broker_account_id', models.CharField(max_length=50, verbose_name='ID инвестиционного счета')),
                ('sync_at', models.DateTimeField(default=datetime.datetime(1899, 12, 31, 21, 30, tzinfo=utc), verbose_name='Время последней синхронизации')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owned_investment_accounts', to=settings.AUTH_USER_MODEL, verbose_name='Создатель счета')),
            ],
            options={
                'verbose_name': 'Инвестиционный счет',
                'verbose_name_plural': 'Инвестиционные счета',
            },
        ),
    ]
