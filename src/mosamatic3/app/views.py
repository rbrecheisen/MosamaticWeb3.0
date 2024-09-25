from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from wsgiref.util import FileWrapper

from .data.fileuploadprocessor import FileUploadProcessor
from .data.datamanager import DataManager
from .data.dicomstructureanalyzer import DicomStructureAnalyzer


@login_required
def auth(_):
    return HttpResponse(status=200)


@login_required
def filesets(request):
    manager = DataManager()
    if request.method == 'POST':
        file_paths, file_names = FileUploadProcessor().process_upload(request)
        manager.create_fileset_from_files(file_paths, file_names, request.user)
    return render(request, 'filesets.html', context={'filesets': manager.get_filesets(request.user)})


@login_required
def fileset(request, fileset_id):
    manager = DataManager()
    action = None
    if request.method == 'GET':
        fs = manager.get_fileset(fileset_id)
        action = request.GET.get('action', None)
        if action == 'download':
            zip_file_path = manager.get_zip_file_from_fileset(fs)
            with open(zip_file_path, 'rb') as f:
                response = HttpResponse(FileWrapper(f), content_type='application/zip')
                response['Content-Disposition'] = 'attachment; filename="{}.zip"'.format(fs.name)
            return response
        elif action == 'delete':
            manager.delete_fileset(fs)
            return render(request, 'filesets.html', context={'filesets': manager.get_filesets(request.user)})
        elif action == 'rename':
            fs = manager.rename_fileset(fs, request.GET.get('new_name'))
        elif action == 'make-public':
            fs = manager.make_fileset_public(fs)
        elif action == 'make-private':
            fs = manager.make_fileset_public(fs, public=False)
        elif action == 'view-dicom-structure':
            cohort = manager.get_cohort_for_fileset(fs)
            patients = manager.get_patients_for_cohort(cohort)
            return render(request, 'dicomstructure.html', context={
                'fileset': fs, 'cohort': cohort, 'patients': patients, 'studies': [], 'series': [], 'images': [],
            })
        elif action == 'analyze-dicom-structure':
            analyzer = DicomStructureAnalyzer()
            analyzer.execute(fs)
            cohort = manager.get_cohort_for_fileset(fs)
            patients = manager.get_patients_for_cohort(cohort)
            return render(request, 'dicomstructure.html', context={
                'fileset': fs, 'cohort': cohort, 'patients': patients, 'studies': [], 'series': [], 'images': [],
            })
        else:
            pass
        return render(request, 'fileset.html', context={'fileset': fs, 'files': manager.get_files(fs)})
    return HttpResponseForbidden(f'Wrong method ({request.method}) or action ({action})')


@login_required
def dicomstructure(request, fileset_id):
    manager = DataManager()
    action = None
    if request.method == 'GET':
        fs = manager.get_fileset(fileset_id)
        pass
    return HttpResponseForbidden(f'Wrong method ({request.method}) or action ({action})')


@login_required
def custom_logout(request):
    logout(request)
    return redirect('/')