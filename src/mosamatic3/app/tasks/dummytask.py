import time

from huey.contrib.djhuey import task
from .utils import set_task_progress, delete_task_progress


@task()
def dummytask(task_progress_id):
    name = 'dummytask'
    nr_steps = 5
    failed_step = 3
    for step in range(nr_steps):
        if step == failed_step:
            print(f'Task {name} failed at ({step})...')
            delete_task_progress(name, task_progress_id)
            return False
        print(f'Running {name} ({step})...')
        time.sleep(1)
        progress = int(((step + 1) / (nr_steps)) * 100)
        set_task_progress(name, task_progress_id, progress)
    delete_task_progress(name, task_progress_id)
    return True
