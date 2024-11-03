from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from ...tasks.checkdicomtask import checkdicomtask
from ...tasks.taskmanager import TaskManager
from ...data.datamanager import DataManager
from ...data.logmanager import LogManager

LOG = LogManager()


@login_required
def checkdicom(request):
    data_manager = DataManager()
    task_manager = TaskManager()
    if request.method == 'POST':
        fileset_id = request.POST.get('fileset_id', None)
        if fileset_id:
            output_fileset_name = request.POST.get('output_fileset_name', None)
            return task_manager.run_task_and_get_response(checkdicomtask, fileset_id, output_fileset_name, request.user)
        else:
            LOG.warning(f'no fileset ID in POST request')
            pass
    elif request.method == 'GET':
        response = task_manager.get_response('checkdicomtask', request)
        if response:
            return response
    else:
        pass
    filesets = data_manager.get_filesets(request.user)
    task = data_manager.get_task_by_name('checkdicomtask')
    return render(request, 'tasks/checkdicom.html', context={'filesets': filesets, 'task': task})