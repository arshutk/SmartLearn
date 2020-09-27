# Generated by Django 3.1.1 on 2020-09-26 13:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('userauth', '0008_userprofile_is_teacher'),
        ('classes', '0006_auto_20200926_1737'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answersheet',
            name='assignment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answersheet', to='classes.assignment'),
        ),
        migrations.AlterField(
            model_name='answersheet',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answersheet', to='userauth.userprofile'),
        ),
        migrations.AlterField(
            model_name='assignment',
            name='classroom',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignment', to='classes.classroom'),
        ),
    ]