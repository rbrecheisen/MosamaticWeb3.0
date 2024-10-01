import time

from huey.contrib.djhuey import task
from .utils import set_task_progress, delete_task_progress


@task()
def dummyparamstask(task_progress_id: str, some_param: str) -> bool:
    name = 'dummyparamstask'
    nr_steps = 5
    set_task_progress(name, task_progress_id, 0)
    for step in range(nr_steps):
        print(f'Running {name} with parameter "{some_param}" ({step})...')
        time.sleep(1)
        progress = int(((step + 1) / (nr_steps)) * 100)
        set_task_progress(name, task_progress_id, progress)
    delete_task_progress(name, task_progress_id)
    return True