import time

from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required
from huey.contrib.djhuey import task

from ..utils import set_task_status
from .task import Task
from .taskmanager import TaskManager
from ..data.datamanager import DataManager


class DummyParamsTask(Task):
    def __init__(self) -> None:
        super(DummyParamsTask, self).__init__(
            name='dummyparamstask',
            display_name='Dummy parameter task',
            description='This is a dummy task with parameters',
            html_page='tasks/dummyparams.html',
            url_pattern='/tasks/dummyparams/',
            visible=False,
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
    
    @staticmethod
    @login_required
    def view(request: HttpRequest) -> HttpResponse:
        manager = TaskManager()
        if request.method == 'POST':
            some_param = request.POST.get('some_param', None)
            return manager.run_task_and_get_response(dummyparamstask, some_param)
        elif request.method == 'GET':
            response = manager.get_response('dummyparamstask', request)
            if response:
                return response
        else:
            pass
        data_manager = DataManager()
        task = data_manager.get_task_by_name('dummyparamstask')
        return render(request, 'tasks/dummyparams.html', context={'task': task})        


@task()
def dummyparamstask(task_status_id: str, some_param: str) -> bool:
    return DummyParamsTask().run(task_status_id, some_param)