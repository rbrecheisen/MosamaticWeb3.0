import os
import pydicom
import pydicom.errors
import numpy as np

from huey.contrib.djhuey import task
from .utils import set_task_progress, delete_task_progress
from pydicom.uid import ExplicitVRLittleEndian, ImplicitVRLittleEndian, ExplicitVRBigEndian

from ..data.datamanager import DataManager


def is_compressed(p):
    return p.file_meta.TransferSyntaxUID not in [ExplicitVRLittleEndian, ImplicitVRLittleEndian, ExplicitVRBigEndian]


def process_file(f, data_manager, fileset):
    try:
        p = pydicom.dcmread(f.path)
        if is_compressed(p):
            p.decompress()
        pixel_array = p.pixel_array
        hu_array = pixel_array * p.RescaleSlope + p.RescaleIntercept
        hu_air = -1000
        new_rows = max(p.Rows, p.Columns)
        new_cols = max(p.Rows, p.Columns)
        padded_hu_array = np.full((new_rows, new_cols), hu_air, dtype=hu_array.dtype)
        padded_hu_array[:pixel_array.shape[0], :pixel_array.shape[1]] = hu_array
        pixel_array_padded = (padded_hu_array - p.RescaleIntercept) / p.RescaleSlope
        pixel_array_padded = pixel_array_padded.astype(pixel_array.dtype)
        p.PixelData = pixel_array_padded.tobytes()
        p.Rows = new_rows
        p.Columns = new_rows
        new_file_path = os.path.join(fileset.path, os.path.split(f.path)[1])
        p.save_as(new_file_path)
        data_manager.create_file(new_file_path, fileset)
    except pydicom.errors.InvalidDicomError:
        pass


# https://chatgpt.com/c/66fa806e-1a08-800b-81dd-6fd260753341
@task()
def rescaledicomtask(task_progress_id, fileset_id, user):
    """
    Transforms non-square DICOM image to square image by zero-padding along short axis and scaling down to 512 x 512.

    Arguments:
    - task_progress_id: ID of Redis item containing progress
    - fileset_id: ID of fileset to work on
    - user: Current request user
    
    Returns: True or False
    """
    name = 'rescaledicomtask'
    print(f'name: {name}, task_progress_id: {task_progress_id}, fileset_id: {fileset_id}')
    data_manager = DataManager()
    fileset = data_manager.get_fileset(fileset_id)
    files = data_manager.get_files(fileset)
    new_fileset = data_manager.create_fileset(user)
    nr_steps = len(files)
    for step in range(nr_steps):
        process_file(files[step], data_manager, new_fileset)
        progress = int(((step + 1) / (nr_steps)) * 100)
        set_task_progress(name, task_progress_id, progress)
    delete_task_progress(name, task_progress_id)
    return True