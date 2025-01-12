import pydicom
import pydicom.errors

from typing import Dict
from huey.contrib.djhuey import task
from django.contrib.auth.models import User

from ..utils import is_uuid, set_task_status, is_compressed
from ..data.datamanager import DataManager
from ..data.logmanager import LogManager
from .taskexception import TaskException
from .task import Task

LOG = LogManager()


class ExtractDicomHeadersTask(Task):
    def __init__(self) -> None:
        super(ExtractDicomHeadersTask, self).__init__(
            name='extractdicomheaderstask',
            display_name='Extract DICOM headers task',
            description='This task extracts header info from DICOM images',
            html_page='tasks/extractdicomheaderstask.html',
            url_pattern='/tasks/extractdicomheaderstask',
            task_func=extractdicomheaderstask,
            parameter_names=['fileset_id', 'output_fileset_name'],
            visible=True,
)

    def run(self, task_status_id: str, fileset_id: str, output_fileset_name: str, user :User) -> bool:
        name = self.name
        LOG.info(f'name: {name}, task_status_id: {task_status_id}, fileset_id: {fileset_id}, output_fileset_name: {output_fileset_name}')
        data_manager = DataManager()
        if not is_uuid(fileset_id):
            raise TaskException(f'{name}() fileset_id is not UUID')
        fileset = data_manager.get_fileset(fileset_id)
        files = data_manager.get_files(fileset)
        header_files = []
        nr_steps = len(files)
        set_task_status(name, task_status_id, {'status': 'running', 'progress': 0})
        for step in range(nr_steps):
            LOG.info(f'{name}() processing file {files[step].path}...')
            try:
                p = pydicom.dcmread(files[step].path)
                if is_compressed(p):
                    p.decompress()
                file_path = files[step].path + '_header.txt'
                with open(file_path, 'w') as f:
                    f.write(str(p))
                header_files.append(file_path)
            except pydicom.errors.InvalidDicomError:
                pass
            progress = int(((step + 1) / (nr_steps)) * 100)
            set_task_status(name, task_status_id, {'status': 'running', 'progress': progress})
        if len(header_files) > 0:
            new_fileset = data_manager.create_fileset(user, output_fileset_name)
            for f in header_files:
                data_manager.create_file(f, new_fileset)
        set_task_status(name, task_status_id, {'status': 'completed', 'progress': 100})
        return True
    

@task()
def extractdicomheaderstask(task_status_id: str, task_parameters: Dict[str, str]) -> bool:
    return ExtractDicomHeadersTask().run(
        task_status_id, 
        task_parameters['fileset_id'], 
        task_parameters['output_fileset_name'], 
        task_parameters['user']
    )