# Generated by Django 3.1.1 on 2020-09-26 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauth', '0002_auto_20200926_1906'),
    ]

    operations = [
        migrations.AddField(
            model_name='otpmodel',
            name='is_teacher',
            field=models.BooleanField(default=False),
        ),
    ]