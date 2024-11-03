from django.shortcuts import render
from django.http import HttpResponseNotFound
from django.contrib.auth.decorators import login_required

from ..data.datamanager import DataManager
from ..tasks.taskloader import TaskLoader


@login_required
def tasks(request):
    data_manager = DataManager()
    return render(request, 'tasks/tasks.html', context={'tasks': data_manager.get_tasks()})


@login_required
def task(request, task_name: str):
    task = TaskLoader().load_task(task_name)
    if task:
        return task.view(request)
    return HttpResponseNotFound(f'Task {task_name} not found')