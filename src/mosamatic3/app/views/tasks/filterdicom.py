import logging

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from ...tasks.filterdicomtask import filterdicomtask
from ...tasks.taskmanager import TaskManager
from ...data.datamanager import DataManager


LOG = logging.getLogger('mosamatic3')


@login_required
def filterdicom(request):
    data_manager = DataManager()
    task_manager = TaskManager()
    if request.method == 'POST':
        fileset_id = request.POST.get('fileset_id', None)
        if fileset_id:
            output_fileset_name = request.POST.get('output_fileset_name', None)
            rows = int(request.POST.get('rows', 0))
            cols = int(request.POST.get('cols', 0))
            rows_equals = True if request.POST.get('rows_equals', '0') == '1' else False
            cols_equals = True if request.POST.get('cols_equals', '0') == '1' else False
            return task_manager.run_task_and_get_response(filterdicomtask, fileset_id, output_fileset_name, request.user, rows, cols, rows_equals, cols_equals)
        else:
            print(f'No fileset ID in POST request')
            pass
    elif request.method == 'GET':
        response = task_manager.get_response('filterdicomtask', request)
        if response:
            return response
    else:
        pass
    filesets = data_manager.get_filesets(request.user)
    return render(request, 'tasks/filterdicom.html', context={'filesets': filesets})