import logging
import redis
import uuid

from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from huey.contrib.djhuey import HUEY

from ...tasks.dummyparamstask import dummy_params_task


LOG = logging.getLogger('mosamatic3')
r = redis.Redis(host=settings.REDIS_HOST, port=6379, db=0)


@login_required
def dummyparams(request):
    if request.method == 'POST':
        task_progress_id = str(uuid.uuid4())
        task_result = dummy_params_task(task_progress_id, request.POST.get('some_param', None))
        return JsonResponse({'task_result_id': task_result.id, 'task_progress_id': task_progress_id, 'task_status': 'running', 'progress': 0})
    elif request.method == 'GET':
        task_result_id = request.GET.get('task_result_id', None)
        task_progress_id = request.GET.get('task_progress_id', None)
        if task_result_id:
            progress = r.get(f'dummy_params_task.{task_progress_id}.progress')
            if progress:
                progress = int(progress)
            task_result = HUEY.result(task_result_id)
            if task_result is None:
                return JsonResponse({'task_result_id': task_result_id, 'task_progress_id': task_progress_id, 'task_status': 'running', 'progress': progress})
            else:
                return JsonResponse({'task_result_id': task_result_id, 'task_progress_id': task_progress_id, 'task_status': 'completed', 'progress': 100})
    else:
        pass
    return render(request, 'tasks/dummy_params.html')