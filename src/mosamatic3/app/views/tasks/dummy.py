from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from huey.contrib.djhuey import HUEY

from ...tasks.dummytask import dummy_task


@login_required
def dummy(request):
    # Use TaskModel to also keep track of task progress!!!
    if request.method == 'GET':
        task_id = request.GET.get('task_id', None)
        if task_id:
            # Use TaskManager to handle task creation and retrieval
            task_result = HUEY.result(task_id)
            if task_result is None:
                return JsonResponse({'task_id': task_id, 'task_status': 'running'})
            return JsonResponse({'task_id': task_id, 'task_status': 'complete'})
    elif request.method == 'POST':
        task_result = dummy_task()
        return JsonResponse({'task_id': task_result.id, 'task_status': 'running'})
    else:
        pass
    return render(request, 'tasks/dummy.html')