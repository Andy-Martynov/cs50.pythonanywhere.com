# Generated by Django 3.0.8 on 2020-12-13 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('album', '0002_auto_20201212_1042'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='image',
        ),
        migrations.AlterField(
            model_name='extention',
            name='mode',
            field=models.CharField(choices=[('IMG', 'Image'), ('VID', 'Video'), ('DOC', 'Document'), ('UKN', 'Unknown')], default='IMG', max_length=3),
        ),
        migrations.AlterField(
            model_name='item',
            name='mode',
            field=models.CharField(choices=[('IMG', 'Image'), ('VID', 'Video'), ('DOC', 'Document'), ('UKN', 'Unknown')], default='IMG', max_length=3),
        ),
        migrations.AlterField(
            model_name='item',
            name='thumb',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
