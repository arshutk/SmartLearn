# Generated by Django 3.1.1 on 2020-09-24 19:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauth', '0006_auto_20200924_2038'),
    ]

    operations = [
        migrations.AlterField(
            model_name='otpmodel',
            name='time_created',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]