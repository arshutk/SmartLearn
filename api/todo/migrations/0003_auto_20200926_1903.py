# Generated by Django 3.1.1 on 2020-09-26 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0002_auto_20200926_1737'),
    ]

    operations = [
        migrations.AlterField(
            model_name='todo',
            name='date_time',
            field=models.DateTimeField(null=True),
        ),
    ]