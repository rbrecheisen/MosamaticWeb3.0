import pydicom
import pydicom.errors

from huey.contrib.djhuey import task
from .utils import set_task_progress, delete_task_progress

from ..data.datamanager import DataManager


def process_file(f, rows, cols, rows_equals, cols_equals):
    rows = int(rows)
    cols = int(cols)
    rows_equals = True if rows_equals == '1' else False
    cols_equals = True if cols_equals == '1' else False
    try:
        p = pydicom.dcmread(f.path, stop_before_pixels=True)
        ok = True
        if p.Rows == rows and not rows_equals:
            ok = False
        if p.Columns == cols and not cols_equals:
            ok = False
        return ok
    except pydicom.errors.InvalidDicomError:
        return False


@task()
def filterdicomtask(task_progress_id, fileset_id, user, rows, cols, rows_equals, cols_equals):
    """
    Filters DICOM images based on their dimensions. 

    Arguments:
    - task_progress_id: ID of Redis item containing progress
    - fileset_id: ID of fileset to work on
    - user: Current request user
    - rows: Nr. of rows in image
    - cols: Nr. of columns in image
    - rows_equals: Whether nr. rows in image should be equal or unequal to specified nr. rows
    - cols_equals: Whether nr. columns in image should be equal or unequal to specified nr. columns

    Returns: True or False
    """
    name = 'filterdicomtask'
    print(f'name: {name}, task_progress_id: {task_progress_id}, fileset_id: {fileset_id}, rows: {rows}, cols: {cols}, rows_equals: {rows_equals}, cols_equals: {cols_equals}')
    data_manager = DataManager()
    fileset = data_manager.get_fileset(fileset_id)
    files = data_manager.get_files(fileset)
    new_files = []
    nr_steps = len(files)
    for step in range(nr_steps):
        if not process_file(files[step], rows, cols, rows_equals, cols_equals):
            continue
        else:
            new_files.append(files[step])        
        progress = int(((step + 1) / (nr_steps)) * 100)
        set_task_progress(name, task_progress_id, progress)
    if len(new_files) > 0:
        new_fileset = data_manager.create_fileset(user)
        for f in new_files:
            data_manager.create_file(f.path, new_fileset)
    else:
        print(f'New fileset is empty')
    delete_task_progress(name, task_progress_id)
    return True