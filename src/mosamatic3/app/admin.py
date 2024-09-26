from django.contrib import admin

from .models import FileSetModel


@admin.register(FileSetModel)
class FileSetModelAdmin(admin.ModelAdmin):
    list = ('name', 'path', 'created', 'owner', 'public')