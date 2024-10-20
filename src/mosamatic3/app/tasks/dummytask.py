import time

from huey.contrib.djhuey import task
from ..utils import set_task_progress, delete_task_progress, set_task_status, delete_task_status
from ..data.logmanager import LogManager

LOG = LogManager()


@task()
def dummytask(task_status_id: str) -> bool:
    name = 'dummytask'
    nr_steps = 5
    failed_step = 3
    set_task_status(name, task_status_id, {'status': 'running', 'progress': 0})
    for step in range(nr_steps):
        if step == failed_step:
            LOG.warning(f'Task {name} failed at ({step})...')
            set_task_status(name, task_status_id, {'status': 'failed', 'progress': -1})
            return False
        LOG.info(f'Running {name} ({step})...')
        time.sleep(1)
        progress = int(((step + 1) / (nr_steps)) * 100)
        set_task_status(name, task_status_id, {'status': 'running', 'progress': progress})
    set_task_status(name, task_status_id, {'status': 'completed', 'progress': 100})
    return True
