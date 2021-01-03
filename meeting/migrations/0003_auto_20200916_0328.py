# Generated by Django 3.0.8 on 2020-09-16 03:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meeting', '0002_location_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='image',
            field=models.ImageField(blank=True, default='meeting/images/big_pin.png', null=True, upload_to='meeting/images/'),
        ),
        migrations.AlterField(
            model_name='location',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=16, default=0, max_digits=19, null=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=16, default=0, max_digits=19, null=True),
        ),
    ]
