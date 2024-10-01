import os
import pydicom
import pydicom.errors
import numpy as np

from scipy.ndimage import zoom
from huey.contrib.djhuey import task
from django.contrib.auth.models import User
from pydicom.uid import ExplicitVRLittleEndian, ImplicitVRLittleEndian, ExplicitVRBigEndian
from .utils import set_task_progress, delete_task_progress
from ..models import FileSetModel
from ..data.datamanager import DataManager


def is_compressed(p: pydicom.FileDataset) -> bool:
    return p.file_meta.TransferSyntaxUID not in [ExplicitVRLittleEndian, ImplicitVRLittleEndian, ExplicitVRBigEndian]


def rescale_image_to_512x512(f, data_manager: DataManager, fileset: FileSetModel) -> bool:
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
        pixel_array_padded = pixel_array_padded.astype(pixel_array.dtype) # Image now has largest dimensions
        pixel_array_rescaled = zoom(pixel_array_padded, zoom=(512 / new_rows), order=3) # Cubic interpolation
        pixel_array_rescaled = pixel_array_rescaled.astype(pixel_array.dtype)
        original_pixel_spacing = p.PixelSpacing
        new_pixel_spacing = [ps * (new_rows / 512) for ps in original_pixel_spacing]
        p.PixelSpacing = new_pixel_spacing
        p.PixelData = pixel_array_rescaled.tobytes()
        p.Rows = 512
        p.Columns = 512
        new_file_path = os.path.join(fileset.path, os.path.split(f.path)[1])
        p.save_as(new_file_path)
        data_manager.create_file(new_file_path, fileset)
        return True
    except pydicom.errors.InvalidDicomError:
        return False


# https://chatgpt.com/c/66fa806e-1a08-800b-81dd-6fd260753341
@task()
def rescaledicomtask(task_progress_id: str, fileset_id: str, output_fileset_name: str, user: User) -> bool:
    """
    Transforms non-square DICOM image to square image by zero-padding along short axis and scaling down to 512 x 512.

    Parameters:
    task_progress_id (str): ID of Redis item containing progress.
    fileset_id (str): ID of fileset to work on.
    user (User): Current request user.
    
    Returns:
    bool: Whether task has completed or failed.
    """
    name = 'rescaledicomtask'
    print(f'name: {name}, task_progress_id: {task_progress_id}, fileset_id: {fileset_id}, output_fileset_name: {output_fileset_name}')
    data_manager = DataManager()
    fileset = data_manager.get_fileset(fileset_id)
    files = data_manager.get_files(fileset)
    new_fileset = data_manager.create_fileset(user, output_fileset_name)
    nr_steps = len(files)
    for step in range(nr_steps):
        if rescale_image_to_512x512(files[step], data_manager, new_fileset):
            progress = int(((step + 1) / (nr_steps)) * 100)
            set_task_progress(name, task_progress_id, progress)
        else:
            print(f'Could not rescale image {files[step].path}, skipping...')
    delete_task_progress(name, task_progress_id)
    return True