import os
import shutil

from typing import List
from os.path import basename
from zipfile import ZipFile
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q

from ..models import FileModel, FileSetModel
# from .pngimagegenerator import PngImageGenerator


class DataManager:
    def __init__(self):
        pass

    @staticmethod
    def create_file(path, fileset: FileSetModel) -> FileModel:
        # generator = PngImageGenerator()
        # png_path = generator.run(path) # Return None if no PNG creation possible for this file type
        # return FileModel.objects.create(
        #     name=os.path.split(path)[1], path=path, png_path=png_path, fileset=fileset)
        return FileModel.objects.create(
            name=os.path.split(path)[1], path=path, fileset=fileset)
    
    @staticmethod
    def create_fileset(user: User, name: str=None) -> FileSetModel:
        if name:
            fs_name = name
        else:
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S.%f')
            fs_name = 'fileset-{}'.format(timestamp)
        fileset = FileSetModel.objects.create(name=fs_name, owner=user) # fileset.path is set in post_save() for FileSetModel
        return fileset
    
    def create_fileset_from_files(self, file_paths: List[str], file_names: List[str], fileset_name: str, user: User) -> FileSetModel:
        if len(file_paths) == 0 or len(file_names) == 0:
            return None
        fileset = self.create_fileset(user, fileset_name)
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
    def get_filesets(user: User) -> List[FileSetModel]:
        if not user.is_staff:
            return FileSetModel.objects.filter(Q(owner=user) | Q(public=True))
        return FileSetModel.objects.all()

    @staticmethod
    def get_fileset(fileset_id: str) -> FileSetModel:
        return FileSetModel.objects.get(pk=fileset_id)
    
    @staticmethod
    def get_files(fileset: FileSetModel) -> List[FileModel]:
        return FileModel.objects.filter(fileset=fileset).all()

    @staticmethod
    def delete_fileset(fileset: FileSetModel):
        fileset.delete()

    @staticmethod
    def rename_fileset(fileset: FileSetModel, new_name: str):
        fileset.name = new_name
        fileset.save()
        return fileset

    @staticmethod
    def make_dataset_public(fileset: FileSetModel, public: bool=True) -> FileSetModel:
        fileset.public = public
        fileset.save()
        return fileset
    
    def get_zip_file_from_fileset(self, fileset: FileSetModel) -> str:
        files = self.get_files(fileset)
        zip_file_path = os.path.join(fileset.path, '{}.zip'.format(fileset.name))
        with ZipFile(zip_file_path, 'w') as zip_obj:
            for f in files:
                zip_obj.write(f.path, arcname=basename(f.path))
                if f.png_path: # Also add any PNG image for this file
                    zip_obj.write(f.png_path, arcname=basename(f.png_path))
        return zip_file_path