from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from ...tasks.totalsegmentatortask import totalsegmentatortask
from ...tasks.taskmanager import TaskManager
from ...data.datamanager import DataManager
from ...data.logmanager import LogManager

LOG = LogManager()


@login_required
def totalsegmentator(request):
    data_manager = DataManager()
    task_manager = TaskManager()
    if request.method == 'POST':
        fileset_id = request.POST.get('fileset_id', None)
        if fileset_id:
            output_fileset_name = request.POST.get('output_fileset_name', None)
            return task_manager.run_task_and_get_response(
                totalsegmentatortask, fileset_id, output_fileset_name, request.user)
        else:
            LOG.warning(f'views.tasks.totalsegmentator: no segmentation fileset ID selected')
    elif request.method == 'GET':
        response = task_manager.get_response('totalsegmentatortask', request)
        if response:
            return response
    else:
        pass
    filesets = data_manager.get_filesets(request.user)
    return render(request, 'tasks/totalsegmentator.html', context={'filesets': filesets})