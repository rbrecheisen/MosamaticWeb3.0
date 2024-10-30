from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from ...data.datamanager import DataManager


@login_required
def tasks(request):
    data_manager = DataManager()
    return render(request, 'tasks/tasks.html', context={'tasks': data_manager.get_tasks()})