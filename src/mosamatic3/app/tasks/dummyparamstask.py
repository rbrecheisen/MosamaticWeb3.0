import time
import redis

from django.conf import settings
from huey.contrib.djhuey import task

r = redis.Redis(host=settings.REDIS_HOST, port=6379, db=0)


@task()
def dummy_params_task(task_progress_id, some_param):
    nr_steps = 5
    redis_key = f'dummy_params_task.{task_progress_id}.progress'
    for step in range(nr_steps):
        print(f'Running dummy params task with param {some_param} ({step})...')
        time.sleep(1)
        progress = int(((step + 1) / (nr_steps)) * 100)
        r.set(redis_key, progress)
    r.delete(redis_key)
    return True