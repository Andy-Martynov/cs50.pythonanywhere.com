# Generated by Django 3.0.8 on 2020-12-11 11:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Album',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=200, null=True)),
                ('text', models.TextField(blank=True, null=True)),
                ('tag', models.CharField(blank=True, max_length=200, null=True)),
                ('thumb', models.ImageField(blank=True, default='album/images/album_240.png', null=True, upload_to='album/images/')),
                ('image', models.ImageField(blank=True, null=True, upload_to='album/images/')),
                ('def_thumb_width', models.IntegerField(default=240)),
                ('def_thumb_height', models.IntegerField(default=180)),
                ('level', models.IntegerField(default=0)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='childs', to='album.Album')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='albums', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=200, null=True)),
                ('text', models.TextField(blank=True, null=True)),
                ('mode', models.CharField(choices=[('IMG', 'Image'), ('VID', 'Video'), ('DOC', 'Document')], default='IMG', max_length=3)),
                ('tag', models.CharField(blank=True, max_length=200, null=True)),
                ('thumb', models.ImageField(blank=True, default='album/items/images/item_240.png', null=True, upload_to='album/items/images/')),
                ('image', models.ImageField(blank=True, null=True, upload_to='album/items/images/')),
                ('file', models.FileField(blank=True, null=True, upload_to='album/items/images/')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('album', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='album.Album')),
            ],
        ),
    ]
