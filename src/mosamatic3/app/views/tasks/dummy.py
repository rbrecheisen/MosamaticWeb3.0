import logging

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from ...tasks.dummytask import dummytask
from ...tasks.taskmanager import TaskManager
from ...data.datamanager import DataManager
from ...data.logmanager import LogManager

LOG = LogManager()


@login_required
def dummy(request):
    manager = TaskManager()
    if request.method == 'POST':
        return manager.run_task_and_get_response(dummytask)
    elif request.method == 'GET':
        response = manager.get_response('dummytask', request)
        if response:
            return response
    else:
        pass
    data_manager = DataManager()
    task = data_manager.get_task_by_name('dummytask')
    return render(request, task.html_page, context={'task': task})