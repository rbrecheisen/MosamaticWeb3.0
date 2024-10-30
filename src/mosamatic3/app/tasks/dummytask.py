import time

from huey.contrib.djhuey import task
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required

from ..utils import set_task_status
from ..data.logmanager import LogManager
from ..data.datamanager import DataManager
from .taskmanager import TaskManager
from .task import Task

LOG = LogManager()


class DummyTask(Task):
    def __init__(self) -> None:
        super(DummyTask, self).__init__(
            name='dummytask', 
            display_name='Dummy Task', 
            description='This is a dummy task',
            html_page='tasks/dummy.html',
            url_pattern='/tasks/dummy/',
            visible=False,
        )

    def run(self, task_status_id: str) -> bool:
        nr_steps = 5
        failed_step = 3
        set_task_status(self.name, task_status_id, {'status': 'running', 'progress': 0})
        for step in range(nr_steps):
            if step == failed_step:
                LOG.warning(f'Task {self.name} failed at ({step})...')
                set_task_status(self.name, task_status_id, {'status': 'failed', 'progress': -1})
                return False
            LOG.info(f'Running {self.name} ({step})...')
            time.sleep(1)
            progress = int(((step + 1) / (nr_steps)) * 100)
            set_task_status(self.name, task_status_id, {'status': 'running', 'progress': progress})
        set_task_status(self.name, task_status_id, {'status': 'completed', 'progress': 100})
        return True
    
    @staticmethod
    @login_required
    def view(request: HttpRequest) -> HttpResponse:
        manager = TaskManager()
        if request.method == 'POST':
            return manager.run_task_and_get_response(dummytask)
        elif request.method == 'GET':
            response = manager.get_response('dummytask', request)
            if response:
                return response
        else:
            pass
        data_manager = DataManager()
        task = data_manager.get_task_by_name('dummytask')
        return render(request, task.html_page, context={'task': task})        


@task()
def dummytask(task_status_id: str) -> bool:
    return DummyTask().run(task_status_id)