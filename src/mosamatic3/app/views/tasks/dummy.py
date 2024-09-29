import logging
import redis
import uuid

from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from huey.contrib.djhuey import HUEY

from ...tasks.dummytask import dummy_task

LOG = logging.getLogger('mosamatic3')
r = redis.Redis(host=settings.REDIS_HOST, port=6379, db=0)


@login_required
def dummy(request):
    if request.method == 'POST':
        task_progress_id = str(uuid.uuid4())
        task_result = dummy_task(task_progress_id)
        return JsonResponse({'task_result_id': task_result.id, 'task_progress_id': task_progress_id, 'task_status': 'running', 'progress': 0})
    elif request.method == 'GET':
        task_result_id = request.GET.get('task_result_id', None)
        task_progress_id = request.GET.get('task_progress_id', None)
        if task_result_id:
            progress = r.get(f'dummy_task.{task_progress_id}.progress')
            if progress:
                progress = int(progress)
            task_result = HUEY.result(task_result_id)
            if task_result is None:
                return JsonResponse({'task_result_id': task_result_id, 'task_progress_id': task_progress_id, 'task_status': 'running', 'progress': progress})
            elif not task_result:
                return JsonResponse({'task_result_id': task_result_id, 'task_progress_id': task_progress_id, 'task_status': 'failed', 'progress': 0})
            else:
                return JsonResponse({'task_result_id': task_result_id, 'task_progress_id': task_progress_id, 'task_status': 'completed', 'progress': 100})
    else:
        pass
    return render(request, 'tasks/dummy.html')