import logging

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from ...tasks.dicomstructuretask import dicomstructuretask
from ...tasks.taskmanager import TaskManager
from ...data.datamanager import DataManager
from ...data.logmanager import LogManager

LOG = LogManager()


@login_required
def dicomstructure(request):
    data_manager = DataManager()
    task_manager = TaskManager()
    if request.method == 'POST':
        fileset_id = request.POST.get('fileset_id', None)
        if fileset_id:
            output_fileset_name = request.POST.get('output_fileset_name', None)
            return task_manager.run_task_and_get_response(dicomstructuretask, fileset_id, output_fileset_name, request.user)
        else:
            LOG.warning(f'views.tasks.filterdicom: no fileset ID in POST request')
            pass
    elif request.method == 'GET':
        response = task_manager.get_response('dicomstructuretask', request)
        if response:
            return response
    else:
        pass
    filesets = data_manager.get_filesets(request.user)
    return render(request, 'tasks/dicomstructure.html', context={'filesets': filesets})