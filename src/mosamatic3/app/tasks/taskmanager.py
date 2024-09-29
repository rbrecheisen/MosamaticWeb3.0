import uuid

from django.http import JsonResponse
from huey.contrib.djhuey import HUEY
from .task import Task


class TaskManager:
    def run_task_and_get_response(self, task_cls, *args):
        task_progress_id = str(uuid.uuid4())
        task_result = task_cls.run(task_progress_id, args)
        return JsonResponse({'task_result_id': task_result.id, 'task_progress_id': task_progress_id, 'task_status': 'running', 'progress': 0})
    
    def get_response(self, task_name, request):
        task_result_id = request.GET.get('task_result_id', None)
        if task_result_id:
            task_progress_id = request.GET.get('task_progress_id', None)
            progress = Task.get_progress(task_name, task_progress_id)
            if progress:
                progress = int(progress)
            task_result = HUEY.result(task_result_id)
            if task_result is None:
                return JsonResponse({'task_result_id': task_result_id, 'task_progress_id': task_progress_id, 'task_status': 'running', 'progress': progress})
            elif not task_result:
                return JsonResponse({'task_result_id': task_result_id, 'task_progress_id': task_progress_id, 'task_status': 'failed', 'progress': 0})
            else:
                return JsonResponse({'task_result_id': task_result_id, 'task_progress_id': task_progress_id, 'task_status': 'completed', 'progress': 100})
        return None
