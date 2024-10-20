from django.contrib import admin

from .models import FileSetModel, LogOutputModel


@admin.register(FileSetModel)
class FileSetModelAdmin(admin.ModelAdmin):
    list = ('name', 'path', 'created', 'owner', 'public')


@admin.register(LogOutputModel)
class LogOutputModelAdmin(admin.ModelAdmin):
    list = ('timestamp', 'message')