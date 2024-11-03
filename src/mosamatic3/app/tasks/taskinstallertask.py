from huey.contrib.djhuey import task
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required

from .task import Task
from .taskmanager import TaskManager
from .taskexception import TaskException
from ..utils import is_uuid, set_task_status
from ..data.logmanager import LogManager
from ..data.datamanager import DataManager

LOG = LogManager()


class TaskInstallerTask(Task):
    def __init__(self) -> None:
        super(TaskInstallerTask, self).__init__(
            name='taskinstallertask',
            display_name='Task Installer',
            description='Installs new task from a previously uploaded file set',
            html_page='tasks/taskinstallertask.html',
            url_pattern='/tasks/taskinstallertask',
            visible=True,
        )

    def run(self, task_status_id: str, fileset_id: str) -> bool:
        name = self.name
        LOG.info(f'name: {name}, task_status_id: {task_status_id}, fileset_id: {fileset_id}')
        data_manager = DataManager()
        if not is_uuid(fileset_id):
            raise TaskException(f'{name}() fileset_id is not UUID')
        fileset = data_manager.get_fileset(fileset_id)
        files = data_manager.get_files(fileset)
        nr_steps = len(files)
        set_task_status(name, task_status_id, {'status': 'running', 'progress': 0})
        for step in range(nr_steps):

            ########################
            # COPY FILES AND ALSO CREATE NEW TASK MODEL!!!!!!!
            ########################
            LOG.info(f'Installing file {files[step].path}...')

            progress = int(((step + 1) / (nr_steps)) * 100)
            set_task_status(name, task_status_id, {'status': 'running', 'progress': progress})
        set_task_status(name, task_status_id, {'status': 'completed', 'progress': 100})
        return True

    @staticmethod
    @login_required
    def view(request: HttpRequest) -> HttpResponse:
        data_manager = DataManager()
        task_manager = TaskManager()
        if request.method == 'POST':
            fileset_id = request.POST.get('fileset_id', None)
            if fileset_id:
                return task_manager.run_task_and_get_response(taskinstallertask, fileset_id)
            else:
                LOG.warning(f'no fileset ID in POST request')
                pass
        elif request.method == 'GET':
            response = task_manager.get_response('taskinstallertask', request)
            if response:
                return response
        else:
            pass
        filesets = data_manager.get_filesets(request.user)
        task = data_manager.get_task_by_name('taskinstallertask')
        return render(request, task.html_page, context={'filesets': filesets, 'task': task})


@task()
def taskinstallertask(task_status_id: str, fileset_id: str) -> bool:
    return TaskInstallerTask().run(task_status_id, fileset_id)