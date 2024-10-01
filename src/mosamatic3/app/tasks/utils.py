import redis
from django.conf import settings


r = redis.Redis(host=settings.REDIS_HOST, port=6379, db=0)


def get_task_progress(name, task_progress_id: str) -> int:
    progress = r.get(f'{name}.{task_progress_id}.progress')
    if progress:
        return int(progress)
    return -1


def set_task_progress(name, task_progress_id: str, progress: int) -> None:
    r.set(f'{name}.{task_progress_id}.progress', progress)


def delete_task_progress(name, task_progress_id: str) -> None:
    r.delete(f'{name}.{task_progress_id}.progress')