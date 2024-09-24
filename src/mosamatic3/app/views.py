import os
import uuid
import shutil

from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from django.utils import timezone
from django.db.models import Q
from os.path import basename
from django.conf import settings
from wsgiref.util import FileWrapper
from zipfile import ZipFile

from .models import FileSetModel, FileModel


# Move to separate file or class
def process_uploaded_files(request):
    file_paths = []
    file_names = []
    files = request.POST.getlist('files.path') # Files parameter from NGINX
    if files is None or len(files) == 0:
        files = request.FILES.getlist('files') # Files parameter from Django without NGINX
        if files is None or len(files) == 0:
            raise RuntimeError('File upload without files in either POST or FILES object')
        else:
            for f in files:
                if isinstance(f, TemporaryUploadedFile):
                    file_paths.append(f.temporary_file_path())
                    file_names.append(f.name)
                elif isinstance(f, InMemoryUploadedFile):
                    file_path = default_storage.save('{}'.format(uuid.uuid4()), ContentFile(f.read()))
                    file_path = os.path.join(settings.MEDIA_ROOT, file_path)
                    file_paths.append(file_path)
                    file_names.append(f.name)
                elif isinstance(f, str):
                    file_paths.append(f)
                    file_names.append(os.path.split(f)[1])
                else:
                    raise RuntimeError('Unknown file type {}'.format(type(f)))
    else:
        file_paths = files
        file_names = request.POST.getlist('files.name')
    return file_paths, file_names


# Move to data manager class
def create_fileset(user, name=None):
    if name:
        fs_name = name
    else:
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S.%f')
        fs_name = 'fileset-{}'.format(timestamp)
    fileset = FileSetModel.objects.create(name=fs_name, owner=user) # fileset.path is set in post_save() for FileSetModel
    return fileset


def create_file(path, fileset):
    return FileModel.objects.create(
        name=os.path.split(path)[1], path=path, fileset=fileset)


# Move to data manager class. Loading files by inspecting DICOM header should be another class
def create_fileset_from_files(file_paths, file_names, user):
    if len(file_paths) == 0 or len(file_names) == 0:
        return None
    fileset = create_fileset(user)
    for i in range(len(file_paths)):
        source_path = file_paths[i]
        target_name = file_names[i]
        target_path = os.path.join(fileset.path, target_name)
        if not settings.DOCKER: # Hack: to deal with "file in use" error Windows
            shutil.copy(source_path, target_path)
        else:
            shutil.move(source_path, target_path)
        create_file(path=target_path, fileset=fileset)
    return fileset


# Move to data manager class
def get_filesets(user):
    if not user.is_staff:
        return FileSetModel.objects.filter(Q(owner=user) | Q(public=True))
    return FileSetModel.objects.all()


def get_fileset(fileset_id, user):
    return FileSetModel.objects.get(pk=fileset_id)


def delete_fileset(fileset):
    fileset.delete()


@login_required
def auth(_):
    return HttpResponse(status=200)


@login_required
def progress(_):
    return HttpResponse(status=200)


@login_required
def filesets(request):
    if request.method == 'POST':
        file_paths, file_names = process_uploaded_files(request)
        create_fileset_from_files(file_paths, file_names, request.user)
    return render(request, 'filesets.html', context={'filesets': get_filesets(request.user)})


@login_required
def fileset(request, fileset_id):
    if request.method == 'GET':
        fs = get_fileset(fileset_id, request.user)
        action = request.GET.get('action', None)
        if action == 'delete':
            delete_fileset(fs)
    return render(request, 'filesets.html', context={'filesets': get_filesets(request.user)})