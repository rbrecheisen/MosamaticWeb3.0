import logging

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from ...tasks.dummyparamstask import dummyparamstask
from ...tasks.taskmanager import TaskManager


LOG = logging.getLogger('mosamatic3')


@login_required
def dummyparams(request):
    manager = TaskManager()
    if request.method == 'POST':
        some_param = request.POST.get('some_param', None)
        return manager.run_task_and_get_response(dummyparamstask, some_param)
    elif request.method == 'GET':
        response = manager.get_response('dummyparamstask', request)
        if response:
            return response
    else:
        pass
    return render(request, 'tasks/dummyparams.html')