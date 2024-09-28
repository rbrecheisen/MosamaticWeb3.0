from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from ...tasks.taskmanager import TaskManager


@login_required
def dummy(request):
    manager = TaskManager()
    if request.method == 'GET':
        task_result_id = request.GET.get('task_result_id', None)
        print(f'GET: task_result_id = {task_result_id}')
        if task_result_id:
            task_progress = manager.get_task_progress(task_result_id)
            if task_progress:
                return JsonResponse({'task_result_id': task_result_id, 'task_status': task_progress.status, 'task_progress': task_progress.progress})
    elif request.method == 'POST':
        task_result = manager.start_dummy_task()
        print(f'POST: task_result_id = {task_result.id}')
        return JsonResponse({'task_result_id': task_result.id, 'task_status': 'unknown', 'task_progress': 0})
    else:
        pass
    return render(request, 'tasks/dummy.html')