import time
from huey.contrib.djhuey import task
from .task import Task


class DummyTask(Task):
    @task()
    @staticmethod
    def run(task_progress_id, *args):
        name = 'dummytask'
        nr_steps = 5
        failed_step = 3
        for step in range(nr_steps):
            if step == failed_step:
                print(f'Task {name} failed at ({step})...')
                Task.delete_progress(name, task_progress_id)
                return False
            print(f'Running {name} ({step})...')
            time.sleep(1)
            progress = int(((step + 1) / (nr_steps)) * 100)
            Task.set_progress(name, task_progress_id, progress)
        Task.delete_progress(name, task_progress_id)
        return True