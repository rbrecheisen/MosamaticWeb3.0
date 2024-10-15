import uuid

from django.http import JsonResponse, HttpRequest, HttpResponse
from huey.contrib.djhuey import HUEY
from ..utils import get_task_progress, get_task_status


class TaskManager:
    def run_task_and_get_response(self, task_func, *args) -> JsonResponse:
        # task_progress_id = str(uuid.uuid4())
        task_status_id = str(uuid.uuid4())
        # task_result = task_func(task_progress_id, *args)
        task_result = task_func(task_status_id, *args)
        # return JsonResponse({'task_result_id': task_result.id, 'task_progress_id': task_progress_id, 'task_status': 'running', 'progress': 0})
        return JsonResponse({'task_result_id': task_result.id, 'task_status_id': task_status_id, 'task_status': None, 'progress': 0})
    
    def get_response(self, task_name: str, request: HttpRequest) -> JsonResponse:
        task_result_id = request.GET.get('task_result_id', None)
        if task_result_id:
            # task_progress_id = request.GET.get('task_progress_id', None)
            task_status_id = request.GET.get('task_status_id', None)
            # progress = get_task_progress(task_name, task_progress_id)
            task_status = get_task_status(task_name, task_status_id)
            status, progress = None, -1
            if task_status:
                progress, status = task_status['progress'], task_status['status']
            return JsonResponse({'task_result_id': task_result_id, 'task_status_id': task_status_id, 'task_status': status, 'progress': progress})
            # task_result = HUEY.result(task_result_id)
            # if task_result is None:
            #     if progress == 0:
            #         return JsonResponse({'task_result_id': task_result_id, 'task_progress_id': task_progress_id, 'task_status': 'initializing', 'progress': progress})
            #     else:
            #         return JsonResponse({'task_result_id': task_result_id, 'task_progress_id': task_progress_id, 'task_status': 'running', 'progress': progress})
            # elif not task_result:
            #     return JsonResponse({'task_result_id': task_result_id, 'task_progress_id': task_progress_id, 'task_status': 'failed', 'progress': -1})
            # else:
            #     return JsonResponse({'task_result_id': task_result_id, 'task_progress_id': task_progress_id, 'task_status': 'completed', 'progress': 100})
        return None
