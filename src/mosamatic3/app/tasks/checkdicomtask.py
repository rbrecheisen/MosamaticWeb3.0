import pydicom
import pydicom.errors

from huey.contrib.djhuey import task
from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required

from .taskmanager import TaskManager
from ..utils import is_uuid, set_task_status
from ..data.datamanager import DataManager
from ..data.logmanager import LogManager
from .taskexception import TaskException
from .task import Task

LOG = LogManager()


class CheckDicomTask(Task):
    def __init__(self) -> None:
        super(CheckDicomTask, self).__init__(
            name='checkdicomtask',
            display_name='Check DICOM task',
            description='This task checks whether DICOM images are 512 x 512 pixels',
            html_page='tasks/checkdicomtask.html',
            url_pattern='/tasks/checkdicomtask',
            visible=True, installed=False,
)

    @staticmethod
    def process_file(f) -> bool:
        try:
            p = pydicom.dcmread(f.path, stop_before_pixels=True)
            LOG.info(f'file: {f.path}, p.Rows: {p.Rows}, p.Columns: {p.Columns}')
            ok = True
            if p.Rows != 512 or p.Columns != 512:
                LOG.info(f'Image {f.path} has dimensions {p.Rows} x {p.Columns} (should be 512 x 512)')
                ok = False
            return ok
        except pydicom.errors.InvalidDicomError:
            return False
        
    def run(self, task_status_id: str, fileset_id: str, output_fileset_name: str, user :User) -> bool:
        name = self.name
        LOG.info(f'name: {name}, task_status_id: {task_status_id}, fileset_id: {fileset_id}, output_fileset_name: {output_fileset_name}')
        data_manager = DataManager()
        if not is_uuid(fileset_id):
            raise TaskException(f'{name}() fileset_id is not UUID')
        fileset = data_manager.get_fileset(fileset_id)
        files = data_manager.get_files(fileset)
        new_files, wrong_files = [], []
        nr_steps = len(files)
        set_task_status(name, task_status_id, {'status': 'running', 'progress': 0})
        for step in range(nr_steps):
            LOG.info(f'{name}() processing file {files[step].path}...')
            if not self.process_file(files[step]):
                wrong_files.append(files[step])
            else:
                new_files.append(files[step])        
            progress = int(((step + 1) / (nr_steps)) * 100)
            set_task_status(name, task_status_id, {'status': 'running', 'progress': progress})
        if len(new_files) > 0:
            new_fileset = data_manager.create_fileset(user, output_fileset_name)
            for f in new_files:
                data_manager.create_file(f.path, new_fileset)
        if len(wrong_files) > 0:
            wrong_fileset = data_manager.create_fileset(user, output_fileset_name + '-not512x512')
            for f in wrong_files:
                data_manager.create_file(f.path, wrong_fileset)
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
                output_fileset_name = request.POST.get('output_fileset_name', None)
                return task_manager.run_task_and_get_response(checkdicomtask, fileset_id, output_fileset_name, request.user)
            else:
                LOG.warning(f'no fileset ID in POST request')
                pass
        elif request.method == 'GET':
            response = task_manager.get_response('checkdicomtask', request)
            if response:
                return response
        else:
            pass
        filesets = data_manager.get_filesets(request.user)
        task = data_manager.get_task_by_name('checkdicomtask')
        return render(request, task.html_page, context={'filesets': filesets, 'task': task})


@task()
def checkdicomtask(task_status_id: str, fileset_id: str, output_fileset_name: str, user :User) -> bool:
    return CheckDicomTask().run(task_status_id, fileset_id, output_fileset_name, user)