import uuid

from django.http import JsonResponse, HttpRequest
from huey.contrib.djhuey import HUEY
from ..utils import get_task_progress


class TaskManager:
    def run_task_and_get_response(self, task_func, *args) -> JsonResponse:
        task_progress_id = str(uuid.uuid4())
        task_result = task_func(task_progress_id, *args)
        return JsonResponse({'task_result_id': task_result.id, 'task_progress_id': task_progress_id, 'task_status': 'running', 'progress': 0})
    
    def get_response(self, task_name: str, request: HttpRequest) -> JsonResponse:
        task_result_id = request.GET.get('task_result_id', None)
        if task_result_id:
            task_progress_id = request.GET.get('task_progress_id', None)
            progress = get_task_progress(task_name, task_progress_id)
            task_result = HUEY.result(task_result_id)
            if task_result is None:
                if progress == 0:
                    return JsonResponse({'task_result_id': task_result_id, 'task_progress_id': task_progress_id, 'task_status': 'initializing', 'progress': progress})
                else:
                    return JsonResponse({'task_result_id': task_result_id, 'task_progress_id': task_progress_id, 'task_status': 'running', 'progress': progress})
            elif not task_result:
                return JsonResponse({'task_result_id': task_result_id, 'task_progress_id': task_progress_id, 'task_status': 'failed', 'progress': -1})
            else:
                return JsonResponse({'task_result_id': task_result_id, 'task_progress_id': task_progress_id, 'task_status': 'completed', 'progress': 100})
        return None
