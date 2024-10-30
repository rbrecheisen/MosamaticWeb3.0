import time

from huey.contrib.djhuey import task
from ..utils import set_task_progress, delete_task_progress, set_task_status
from .task import Task


class DummyParamsTask(Task):
    def __init__(self) -> None:
        super(DummyParamsTask, self).__init__(
            name='dummyparamstask',
            display_name='Dummy parameter task',
            description='This is a dummy task with parameters',
            html_page='tasks/dummyparams.html',
            url_pattern='tasks/dummyparams/',
        )

    def run(self, task_status_id: str, some_param: str) -> bool:
        name = self.name
        nr_steps = 5
        set_task_status(name, task_status_id, {'status': 'running', 'progress': 0})
        for step in range(nr_steps):
            print(f'Running {name} with parameter "{some_param}" ({step})...')
            time.sleep(1)
            progress = int(((step + 1) / (nr_steps)) * 100)
            set_task_status(name, task_status_id, {'status': 'running', 'progress': progress})
        set_task_status(name, task_status_id, {'status': 'completed', 'progress': 100})
        return True


@task()
def dummyparamstask(task_status_id: str, some_param: str) -> bool:
    return DummyParamsTask().run(task_status_id, some_param)