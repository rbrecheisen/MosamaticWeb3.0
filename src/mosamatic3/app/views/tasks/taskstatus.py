from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from ...tasks.dummytask import dummy_task
from ...models import TaskModel


@login_required
def task_status(request, task_id):
    task = TaskModel.objects.get(pk=task_id)
    task_status = task.status
    return JsonResponse({'task_status': task_status})