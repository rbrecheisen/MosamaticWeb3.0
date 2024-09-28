import time
import redis

from django.conf import settings
from huey.contrib.djhuey import task

r = redis.Redis(host=settings.REDIS_HOST, port=6379, db=0)


@task()
def dummy_task():
    nr_steps = 5
    redis_key = 'dummy_task.progress'
    for step in range(nr_steps):
        print(f'Running dummy task ({step})...')
        time.sleep(1)
        progress = int(((step + 1) / (nr_steps)) * 100)
        r.set(redis_key, progress)
    r.delete(redis_key)
    return True