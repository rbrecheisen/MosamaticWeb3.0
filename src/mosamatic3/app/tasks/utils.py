import redis
from django.conf import settings


r = redis.Redis(host=settings.REDIS_HOST, port=6379, db=0)


def get_task_progress(name, task_progress_id):
    return r.get(f'{name}.{task_progress_id}.progress')


def set_task_progress(name, task_progress_id, progress):
    r.set(f'{name}.{task_progress_id}.progress', progress)


def delete_task_progress(name, task_progress_id):
    r.delete(f'{name}.{task_progress_id}.progress')