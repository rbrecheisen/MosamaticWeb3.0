import uuid

from django.http import JsonResponse, HttpRequest, HttpResponse
from huey.contrib.djhuey import HUEY
from ..utils import get_task_progress, get_task_status, delete_task_status


class TaskManager:
    def run_task_and_get_response(self, task_func, *args) -> JsonResponse:
        task_status_id = str(uuid.uuid4())
        task_result = task_func(task_status_id, *args)
        return JsonResponse({'task_result_id': task_result.id, 'task_status_id': task_status_id, 'task_status': None, 'progress': 0})
    
    def get_response(self, task_name: str, request: HttpRequest) -> JsonResponse:
        task_result_id = request.GET.get('task_result_id', None)
        if task_result_id:
            task_status_id = request.GET.get('task_status_id', None)
            task_status = get_task_status(task_name, task_status_id)
            status, progress = None, -1
            if task_status:
                progress, status = task_status['progress'], task_status['status']
                if status == 'completed' or status == 'failed':
                    delete_task_status(task_name, task_result_id)
            return JsonResponse({'task_result_id': task_result_id, 'task_status_id': task_status_id, 'task_status': status, 'progress': progress})
        return None
