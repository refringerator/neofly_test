# Generated by Django 3.0.8 on 2020-08-01 02:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0005_auto_20200801_0444'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flights',
            name='remote_record_id',
            field=models.CharField(max_length=40, null=True, unique=True, verbose_name='Идентификатор записи на полет 1С'),
        ),
    ]