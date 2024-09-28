from huey.contrib.djhuey import HUEY

from .dummytask import dummy_task
from ..models import TaskProgressModel


class TaskManager:
    def __init__(self):
        pass

    def start_dummy_task(self):
        task_progress = TaskProgressModel.objects.create()
        task_result = dummy_task(task_progress.id)
        task_progress.task_result_id = task_result.id
        task_progress.save()
        return task_result

    def get_task_progress(self, task_result_id):
        try:
            task_progress = TaskProgressModel.objects.filter(task_result_id=task_result_id).first()
            return task_progress
        except TaskProgressModel.DoesNotExist:
            return None