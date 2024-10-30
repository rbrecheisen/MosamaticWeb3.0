from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from ...tasks.rescaledicomtask import rescaledicomtask
from ...tasks.taskmanager import TaskManager
from ...data.datamanager import DataManager
from ...data.logmanager import LogManager

LOG = LogManager()


@login_required
def rescaledicom(request):
    data_manager = DataManager()
    task_manager = TaskManager()
    if request.method == 'POST':
        fileset_id = request.POST.get('fileset_id', None)
        if fileset_id:
            output_fileset_name = request.POST.get('output_fileset_name', None)
            return task_manager.run_task_and_get_response(rescaledicomtask, fileset_id, output_fileset_name, request.user, 512)
        else:
            LOG.warning(f'views.tasks.rescaledicom: no fileset ID selected')
            pass
    elif request.method == 'GET':
        response = task_manager.get_response('rescaledicomtask', request)
        if response:
            return response
    else:
        pass
    filesets = data_manager.get_filesets(request.user)
    return render(request, 'tasks/rescaledicom.html', context={'filesets': filesets})