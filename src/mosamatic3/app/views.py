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

from .models import DataSetModel, FileSetModel, FileModel
from .data.dicomdatasetloader import DicomDataSetLoader


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
def create_dataset(user, name=None):
    if name:
        ds_name = name
    else:
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S.%f')
        ds_name = 'dataset-{}'.format(timestamp)
    dataset = DataSetModel.objects.create(name=ds_name, owner=user) # dataset.path is set in post_save() for DataSetModel
    return dataset


# Move to data manager class. Loading files by inspecting DICOM header should be another class
def create_dataset_from_files(file_paths, file_names, user):
    if len(file_paths) == 0 or len(file_names) == 0:
        return None
    dataset = create_dataset(user)
    for i in range(len(file_paths)):
        source_path = file_paths[i]
        target_name = file_names[i]
        target_path = os.path.join(dataset.path, target_name)
        shutil.move(source_path, target_path)
        # create_file_path(path=target_path, dataset=dataset)
    return dataset


# Move to data manager class
def get_datasets(user):
    if not user.is_staff:
        return DataSetModel.objects.filter(Q(owner=user) | Q(public=True))
    return DataSetModel.objects.all()


def get_dataset(dataset_id, user):
    return DataSetModel.objects.get(pk=dataset_id)


def delete_dataset(dataset):
    dataset.delete()


@login_required
def auth(_):
    return HttpResponse(status=200)


@login_required
def progress(_):
    return HttpResponse(status=200)


@login_required
def datasets(request):
    if request.method == 'POST':
        file_paths, file_names = process_uploaded_files(request)
        loader = DicomDataSetLoader()
        loader.load(file_paths, file_names)
        # create_dataset_from_files(file_paths, file_names, request.user)
    return render(request, 'datasets.html', context={'datasets': get_datasets(request.user)})

@login_required
def dataset(request, dataset_id):
    if request.method == 'GET':
        ds = get_dataset(dataset_id, request.user)
        action = request.GET.get('action', None)
        if action == 'delete':
            delete_dataset(ds)
    return render(request, 'datasets.html', context={'datasets': get_datasets(request.user)})