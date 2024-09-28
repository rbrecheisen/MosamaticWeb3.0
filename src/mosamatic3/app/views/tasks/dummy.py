from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse

from ...tasks.dummytask import dummy_task
from ...models import TaskModel


@login_required
def dummy(request):
    if request.method == 'GET':
        return render(request, 'tasks/dummy.html')
    elif request.method == 'POST':
        task_id = dummy_task()
        return JsonResponse({'task_id': task_id})
    else:
        pass
    return render(request, 'tasks/dummy.html')