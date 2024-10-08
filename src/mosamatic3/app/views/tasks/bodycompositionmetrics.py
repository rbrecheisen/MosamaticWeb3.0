from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from ...tasks.bodycompositionmetricstask import bodycompositionmetricstask
from ...tasks.taskmanager import TaskManager
from ...data.datamanager import DataManager
from ...data.logmanager import LogManager

LOG = LogManager()


@login_required
def bodycompositionmetrics(request):
    data_manager = DataManager()
    task_manager = TaskManager()
    if request.method == 'POST':
        fileset_id = request.POST.get('fileset_id', None)
        if fileset_id:
            segmentation_fileset_id = request.POST.get('segmentation_fileset_id', None)
            if segmentation_fileset_id:
                output_fileset_name = request.POST.get('output_fileset_name', None)
                patient_heights_fileset_id = request.POST.get('patient_heights_fileset_id', None)
                return task_manager.run_task_and_get_response(
                    bodycompositionmetricstask, fileset_id, segmentation_fileset_id, patient_heights_fileset_id, output_fileset_name, request.user)
            else:
                LOG.warning(f'views.tasks.bodycompositionmetrics: no model fileset ID selected')
        else:
            LOG.warning(f'views.tasks.bodycompositionmetrics: no fileset ID selected')
    elif request.method == 'GET':
        response = task_manager.get_response('bodycompositionmetricstask', request)
        if response:
            return response
    else:
        pass
    filesets = data_manager.get_filesets(request.user)
    return render(request, 'tasks/bodycompositionmetrics.html', context={'filesets': filesets})