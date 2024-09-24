import os
import uuid

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile


class FileUploadProcessor:
    def __init__(self):
        pass

    def process_upload(self, request):
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