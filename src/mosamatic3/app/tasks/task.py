import redis
from django.conf import settings


r = redis.Redis(host=settings.REDIS_HOST, port=6379, db=0)

class Task:    
    @staticmethod
    def get_progress(name, task_progress_id):
        return r.get(f'{name}.{task_progress_id}.progress')

    @staticmethod
    def set_progress(name, task_progress_id, progress):
        r.set(f'{name}.{task_progress_id}.progress', progress)

    @staticmethod
    def delete_progress(name, task_progress_id):
        r.delete(f'{name}.{task_progress_id}.progress')

    @staticmethod
    def run(task_progress_id, *args):
        raise NotImplementedError('Implement this in child task')