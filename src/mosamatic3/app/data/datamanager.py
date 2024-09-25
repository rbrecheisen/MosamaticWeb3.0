import os
import shutil

from os.path import basename
from zipfile import ZipFile
from django.conf import settings
from django.utils import timezone
from django.db.models import Q

from ..models import FileModel, FileSetModel, PatientCohortModel, PatientModel, DicomStudyModel, DicomSeriesModel, DicomImageModel


class DataManager:
    def __init__(self):
        pass

    # Filesets and files

    @staticmethod
    def create_file(path, fileset):
        return FileModel.objects.create(
            name=os.path.split(path)[1], path=path, fileset=fileset)
    
    @staticmethod
    def create_fileset(user, name=None):
        if name:
            fs_name = name
        else:
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S.%f')
            fs_name = 'fileset-{}'.format(timestamp)
        fileset = FileSetModel.objects.create(name=fs_name, owner=user) # fileset.path is set in post_save() for FileSetModel
        return fileset
        
    def create_fileset_from_files(self, file_paths, file_names, user):
        if len(file_paths) == 0 or len(file_names) == 0:
            return None
        fileset = self.create_fileset(user)
        for i in range(len(file_paths)):
            source_path = file_paths[i]
            target_name = file_names[i]
            target_path = os.path.join(fileset.path, target_name)
            if not settings.DOCKER: # Hack: to deal with "file in use" error Windows
                shutil.copy(source_path, target_path)
            else:
                shutil.move(source_path, target_path)
            self.create_file(target_path, fileset)
        return fileset
    
    @staticmethod
    def get_filesets(user):
        if not user.is_staff:
            return FileSetModel.objects.filter(Q(owner=user) | Q(public=True))
        return FileSetModel.objects.all()

    @staticmethod
    def get_fileset(fileset_id):
        return FileSetModel.objects.get(pk=fileset_id)
    
    @staticmethod
    def get_files(fileset):
        return FileModel.objects.filter(fileset=fileset).all()

    @staticmethod
    def delete_fileset(fileset):
        fileset.delete()

    @staticmethod
    def rename_fileset(fileset, new_name):
        fileset.name = new_name
        fileset.save()
        return fileset

    @staticmethod
    def make_dataset_public(fileset, public=True):
        fileset.public = public
        fileset.save()
        return fileset
    
    def get_zip_file_from_fileset(self, fileset):
        files = self.get_files(fileset)
        zip_file_path = os.path.join(fileset.path, '{}.zip'.format(fileset.name))
        with ZipFile(zip_file_path, 'w') as zip_obj:
            for f in files:
                zip_obj.write(f.path, arcname=basename(f.path))
        return zip_file_path
    
    # DICOM objects

    def get_cohort_for_fileset(self, fileset): # There can be only one cohort for each fileset
        return PatientCohortModel.objects.filter(fileset=fileset).first()

    def get_patients_for_cohort(self, cohort):
        return PatientModel.objects.filter(cohort=cohort).all()

    def get_studies(self):
        return DicomStudyModel.objects.all() # Filter for user?

    def get_studies_for_patient(self, patient):
        return DicomStudyModel.objects.filter(patient=patient).all()

    def get_series(self):
        return DicomSeriesModel.objects.all() # Filter for user?

    def get_series_for_study(self, study):
        return DicomSeriesModel.objects.filter(study=study).all()

    def get_images(self):
        return DicomImageModel.objects.all()

    def get_images_for_series(self, series):
        return DicomImageModel.objects.filter(series=series).all()