from django.contrib import admin

from .models import Folder, FolderShare

admin.site.register(Folder)
admin.site.register(FolderShare)