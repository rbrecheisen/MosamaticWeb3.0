import logging

from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from huey.contrib.djhuey import HUEY

from ...tasks.dummytask import dummy_task
# from ...tasks.taskmanager import TaskManager

LOG = logging.getLogger('mosamatic3')


@login_required
def dummy(request):
    if request.method == 'POST':
        task_result = dummy_task()
        return JsonResponse({'task_result_id': task_result.id, 'task_status': 'unknown'})
    elif request.method == 'GET':
        task_result_id = request.GET.get('task_result_id', None)
        if task_result_id:
            task_result = HUEY.result(task_result_id)
            if task_result is None:
                return JsonResponse({'task_result_id': task_result_id, 'task_status': 'running'})
            else:
                return JsonResponse({'task_result_id': task_result_id, 'task_status': 'completed'})
    else:
        pass
    return render(request, 'tasks/dummy.html')


# @login_required
# def dummy(request):
#     manager = TaskManager()
#     if request.method == 'POST':
#         task_result = manager.start_dummy_task()
#         LOG.info(f'[POST] task_result.id = {task_result.id}')
#         return JsonResponse({'task_result_id': task_result.id, 'task_status': 'unknown', 'task_progress': 0})
#     elif request.method == 'GET':
#         task_result_id = request.GET.get('task_result_id', None)
#         if task_result_id:
#             task_progress = manager.get_task_progress(task_result_id)
#             LOG.info(f'[GET] task_result.id = {task_result_id}, task_progress = {task_progress}')
#             if task_progress:
#                 return JsonResponse({'task_result_id': task_result_id, 'task_status': task_progress.status, 'task_progress': task_progress.progress})
#             else:
#                 LOG.info('task_progress is None')
#         else:
#             LOG.info('task_result_id is None')
#     else:
#         LOG.info('wrong method')
#     return JsonResponse({'task_result_id': 'None', 'task_status': 'unknown', 'task_progress': 0})