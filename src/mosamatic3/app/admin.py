from django.contrib import admin

from .models import FileSetModel, PatientCohortModel, PatientModel, DicomStudyModel, DicomSeriesModel


@admin.register(FileSetModel)
class FileSetModelAdmin(admin.ModelAdmin):
    list = ('name', 'path', 'created', 'owner', 'public')


# No need for FileModelAdmin (too many objects)


@admin.register(PatientCohortModel)
class PatientCohortModelAdmin(admin.ModelAdmin):
    list = ('name', 'fileset')


@admin.register(PatientModel)
class PatientModelAdmin(admin.ModelAdmin):
    list = ('name', 'patient_id', 'cohort')


@admin.register(DicomStudyModel)
class DicomStudyModelAdmin(admin.ModelAdmin):
    list = ('name', 'study_instance_uid', 'patient')


@admin.register(DicomSeriesModel)
class DicomSeriesModelAdmin(admin.ModelAdmin):
    list = ('name', 'modality', 'image_type', 'series_instance_uid', 'study')