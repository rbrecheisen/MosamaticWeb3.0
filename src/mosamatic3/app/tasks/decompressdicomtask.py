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


class DecompressDicomTask(Task):
    def __init__(self) -> None:
        super(DecompressDicomTask, self).__init__(
            name='decompressdicomtask',
            display_name='Decompress DICOM task',
            description='This task decompresses DICOM images such that they can be imported into older versions of Slice-o-matic',
            html_page='tasks/decompressdicomtask.html',
            url_pattern='/tasks/decompressdicomtask',
            task_func=decompressdicomtask,
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
        decompressed_files = []
        nr_steps = len(files)
        set_task_status(name, task_status_id, {'status': 'running', 'progress': 0})
        for step in range(nr_steps):
            LOG.info(f'{name}() processing file {files[step].path}...')
            try:
                p = pydicom.dcmread(files[step].path)
                if is_compressed(p):
                    p.decompress()
                    file_path = files[step].path + '_raw.dcm'
                    p.save_as(file_path)
                    decompressed_files.append(file_path)
            except pydicom.errors.InvalidDicomError:
                pass
            progress = int(((step + 1) / (nr_steps)) * 100)
            set_task_status(name, task_status_id, {'status': 'running', 'progress': progress})
        if len(decompressed_files) > 0:
            new_fileset = data_manager.create_fileset(user, output_fileset_name)
            for f in decompressed_files:
                data_manager.create_file(f, new_fileset)
        set_task_status(name, task_status_id, {'status': 'completed', 'progress': 100})
        return True
    

@task()
def decompressdicomtask(task_status_id: str, task_parameters: Dict[str, str]) -> bool:
    return DecompressDicomTask().run(
        task_status_id, 
        task_parameters['fileset_id'], 
        task_parameters['output_fileset_name'], 
        task_parameters['user']
    )