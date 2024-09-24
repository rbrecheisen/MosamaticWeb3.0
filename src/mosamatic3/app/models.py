import os
import uuid
import shutil

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.dispatch import receiver


# General purpose objects
class FileSetModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=1024, editable=True, null=False)
    path = models.CharField(max_length=2048, editable=False, null=True, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(
        User, editable=False, related_name='+', on_delete=models.CASCADE)
    public = models.BooleanField(default=False, editable=True)

    def __str__(self):
        return self.name


class FileModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=256, editable=False, null=False)
    path = models.CharField(max_length=2048, editable=False, null=False, unique=True)
    fileset = models.ForeignKey(FileSetModel, on_delete=models.CASCADE)

    def __str__(self):
        return os.path.split(str(self.path))[1]
    

# DICOM objects
class PatientCohortModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=1024, unique=True, null=False)
    cohort_id = models.CharField(max_length=1024, unique=True, null=False)


class PatientModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    patient_id = models.CharField(max_length=1024, unique=False, null=False)
    cohort = models.ForeignKey(PatientCohortModel, on_delete=models.CASCADE)


class DicomStudyModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=1024, unique=False, null=False)
    study_instance_uid = models.CharField(max_length=1024, unique=True, null=False)
    patient = models.ForeignKey(PatientModel, on_delete=models.CASCADE)


class DicomSeriesModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=1024, unique=False, null=False)
    series_instance_uid = models.CharField(max_length=1024, unique=True, null=False)
    study = models.ForeignKey(DicomStudyModel, on_delete=models.CASCADE)


class DicomInstanceModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    instance_uid = models.CharField(max_length=1024, unique=True, null=False)
    series = models.ForeignKey(DicomSeriesModel, on_delete=models.CASCADE)
    file = models.ForeignKey(FileModel, on_delete=models.CASCADE)
    

# Miscellaneous
class LogOutputModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    timestamp = models.DateTimeField()
    message = models.CharField(max_length=1024, editable=False, null=False)


# Signals
@receiver(models.signals.post_save, sender=FileSetModel)
def dataset_post_save(sender, instance, **kwargs):
    if not instance.path:
        instance.path = os.path.join(settings.MEDIA_ROOT, str(instance.id))
        os.makedirs(instance.path, exist_ok=False)
        instance.save()


@receiver(models.signals.post_delete, sender=FileSetModel)
def dataset_post_delete(sender, instance, **kwargs):
    if os.path.isdir(instance.path):
        shutil.rmtree(instance.path)
