# Generated by Django 3.0.8 on 2021-01-02 03:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('album', '0015_auto_20210101_1340'),
    ]

    operations = [
        migrations.AddField(
            model_name='animation',
            name='session_key',
            field=models.CharField(default='none', max_length=50),
        ),
    ]