# Generated by Django 3.0.5 on 2020-04-22 07:59

from django.db import migrations, models
import phone_login.models


class Migration(migrations.Migration):

    dependencies = [
        ('phone_login', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='customuser',
            managers=[
                ('objects', phone_login.models.PhoneNumberUserManager()),
            ],
        ),
        migrations.AlterField(
            model_name='customuser',
            name='last_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='last name'),
        ),
    ]
