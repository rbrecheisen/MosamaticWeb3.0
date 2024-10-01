import pydicom
import pydicom.errors

from huey.contrib.djhuey import task
from django.contrib.auth.models import User
from .utils import set_task_progress, delete_task_progress
from ..data.datamanager import DataManager
from ..data.logmanager import LogManager

LOG = LogManager()


def process_file(f) -> bool:
    try:
        p = pydicom.dcmread(f.path)
        return True
    except pydicom.errors.InvalidDicomError:
        return False


@task()
def musclefatsegmentationtask(task_progress_id: str, fileset_id: str, output_fileset_name: str, user :User) -> bool:
    name = 'musclefatsegmentationtask'
    LOG.info(f'name: {name}, task_progress_id: {task_progress_id}, fileset_id: {fileset_id}, output_fileset_name: {output_fileset_name}')
    data_manager = DataManager()
    fileset = data_manager.get_fileset(fileset_id)
    files = data_manager.get_files(fileset)
    new_files = []
    nr_steps = len(files)
    for step in range(nr_steps):
        if not process_file(files[step]):
            continue
        else:
            new_files.append(files[step])        
        progress = int(((step + 1) / (nr_steps)) * 100)
        set_task_progress(name, task_progress_id, progress)
    if len(new_files) > 0:
        new_fileset = data_manager.create_fileset(user, output_fileset_name)
        for f in new_files:
            data_manager.create_file(f.path, new_fileset)
    else:
        LOG.warning(f'New fileset is empty')
    delete_task_progress(name, task_progress_id)
    return True