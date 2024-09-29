import time
from huey.contrib.djhuey import task
from .task import Task


class DummyParamsTask(Task):
    @task()
    @staticmethod
    def run(task_progress_id, some_param):
        name = 'dummyparamstask'
        nr_steps = 5
        for step in range(nr_steps):
            print(f'Running {name} with parameter "{some_param}" ({step})...')
            time.sleep(1)
            progress = int(((step + 1) / (nr_steps)) * 100)
            Task.set_progress(name, task_progress_id, progress)
        Task.delete_progress(name, task_progress_id)
        return True