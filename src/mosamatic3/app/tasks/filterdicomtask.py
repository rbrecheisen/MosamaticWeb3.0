import pydicom
import pydicom.errors

from huey.contrib.djhuey import task
from django.contrib.auth.models import User
from ..utils import set_task_progress, delete_task_progress, is_uuid
from ..data.datamanager import DataManager
from ..data.logmanager import LogManager
from .taskexception import TaskException

LOG = LogManager()


def process_file(f, rows: int, cols: int, rows_equals: bool, cols_equals: bool) -> bool:
    try:
        p = pydicom.dcmread(f.path, stop_before_pixels=True)
        LOG.info(f'rows: {rows}, cols: {cols}, p.Rows: {p.Rows}, p.Columns: {p.Columns}')
        ok = True
        if rows_equals:
            if p.Rows != rows:
                ok = False
        else:
            if p.Rows == rows:
                ok = False
        if cols_equals:
            if p.Columns != cols:
                ok = False
        else:
            if p.Columns == cols:
                ok = False
        return ok
    except pydicom.errors.InvalidDicomError:
        return False


@task()
def filterdicomtask(task_progress_id: str, fileset_id: str, output_fileset_name: str, user :User, rows: int, cols: int, rows_equals: bool, cols_equals: bool) -> bool:
    name = 'filterdicomtask'
    LOG.info(f'name: {name}, task_progress_id: {task_progress_id}, fileset_id: {fileset_id}, output_fileset_name: {output_fileset_name}, rows: {rows}, cols: {cols}, rows_equals: {rows_equals}, cols_equals: {cols_equals}')
    data_manager = DataManager()
    if not is_uuid(fileset_id):
        raise TaskException('musclefatsegmentationtask() fileset_id is not UUID')
    fileset = data_manager.get_fileset(fileset_id)
    files = data_manager.get_files(fileset)
    new_files = []
    nr_steps = len(files)
    set_task_progress(name, task_progress_id, 0)
    for step in range(nr_steps):
        if not process_file(files[step], rows, cols, rows_equals, cols_equals):
            continue
        else:
            new_files.append(files[step])        
        progress = int(((step + 1) / (nr_steps)) * 100)
        set_task_progress(name, task_progress_id, progress)
    if len(new_files) > 0:
        data_manager.create_fileset_from_files(new_files, output_fileset_name, user)
    else:
        LOG.warning(f'New fileset is empty')
    delete_task_progress(name, task_progress_id)
    return True