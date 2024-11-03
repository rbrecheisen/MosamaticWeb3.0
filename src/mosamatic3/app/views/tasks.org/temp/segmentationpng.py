from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from ...tasks.segmentationpngtask import segmentationpngtask
from ...tasks.taskmanager import TaskManager
from ...data.datamanager import DataManager
from ...data.logmanager import LogManager

LOG = LogManager()


@login_required
def segmentationpng(request):
    data_manager = DataManager()
    task_manager = TaskManager()
    if request.method == 'POST':
        segmentation_fileset_id = request.POST.get('segmentation_fileset_id', None)
        if segmentation_fileset_id:
            output_fileset_name = request.POST.get('output_fileset_name', None)
            return task_manager.run_task_and_get_response(
                segmentationpngtask, segmentation_fileset_id, output_fileset_name, request.user)
        else:
            LOG.warning(f'no segmentation fileset ID selected')
    elif request.method == 'GET':
        response = task_manager.get_response('segmentationpngtask', request)
        if response:
            return response
    else:
        pass
    filesets = data_manager.get_filesets(request.user)
    task = data_manager.get_task_by_name('segmentationpngtask')
    return render(request, 'tasks/segmentationpng.html', context={'filesets': filesets, 'task': task})