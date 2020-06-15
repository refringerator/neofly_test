# Generated by Django 3.0.5 on 2020-06-13 04:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('phone_login', '0003_customuser_deposit_available'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='deposit_available',
            new_name='is_deposit_available',
        ),
        migrations.AddField(
            model_name='customuser',
            name='deposit_minutes',
            field=models.IntegerField(default=0),
        ),
    ]
