# Generated by Django 3.0.8 on 2020-08-01 01:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('phone_login', '0005_auto_20200716_0352'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='phonetoken',
            options={'verbose_name': 'Одноразовый токен', 'verbose_name_plural': 'Одноразовые токены'},
        ),
    ]
