import os
import uuid
import shutil

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.dispatch import receiver


class FileSetModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=1024, editable=True, null=False)
    path = models.CharField(max_length=2048, editable=False, null=True, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(
        User, editable=False, related_name='+', on_delete=models.CASCADE)
    public = models.BooleanField(default=False, editable=True)

    @property
    def size(self):
        return FileModel.objects.filter(fileset=self).count()
    
    @property
    def file_paths(self):
        file_paths = []
        for f in FileModel.objects.filter(fileset=self).all():
            file_paths.append(f.path)
        return file_paths

    def __str__(self):
        return self.name


class FileModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=256, editable=False, null=False)
    path = models.CharField(max_length=2048, editable=False, null=False, unique=False) # unique=False because multiple filesets may refer to same file
    png_path = models.CharField(max_length=2048, editable=False, null=True, unique=False, default=None)
    fileset = models.ForeignKey(FileSetModel, on_delete=models.CASCADE)

    def __str__(self):
        return os.path.split(str(self.path))[1]
    

class LogOutputModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    mode = models.CharField(max_length=8, editable=False, null=False, choices=[
        ('info', 'info'),
        ('warning', 'warning'),
        ('error', 'error'),
    ], default='info')
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.CharField(max_length=1024, editable=False, null=False)

    def __str__(self):
        return f'[{self.timestamp}] - [{self.mode}]: {self.message}'
    

class TaskModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=256, editable=False, null=False)
    display_name = models.CharField(max_length=256, editable=False, null=False)
    description = models.TextField(null=False)
    html_page = models.CharField(max_length=512, editable=False, null=False)
    url_pattern = models.CharField(max_length=1024, editable=False, null=False)
    visible = models.BooleanField(default=True)

    def __str__(self):
        return f'[{self.name}] {self.url_pattern}'


@receiver(models.signals.post_save, sender=FileSetModel)
def fileset_post_save(sender, instance, **kwargs):
    if not instance.path:
        instance.path = os.path.join(settings.MEDIA_ROOT, str(instance.id))
        os.makedirs(instance.path, exist_ok=False)
        instance.save()


@receiver(models.signals.post_delete, sender=FileSetModel)
def fileset_post_delete(sender, instance, **kwargs):
    if os.path.isdir(instance.path):
        shutil.rmtree(instance.path)
