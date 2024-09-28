from django.contrib import admin

from .models import FileSetModel, TaskProgressModel, LogOutputModel


@admin.register(FileSetModel)
class FileSetModelAdmin(admin.ModelAdmin):
    list = ('name', 'path', 'created', 'owner', 'public')


@admin.register(TaskProgressModel)
class TaskProgressModelAdmin(admin.ModelAdmin):
    list = ('task_result_id', 'progress', 'status')


@admin.register(LogOutputModel)
class LogOutputModelAdmin(admin.ModelAdmin):
    list = ('timestamp', 'message')