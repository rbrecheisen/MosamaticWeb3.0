import os
import pydicom
import pydicom.errors
import numpy as np

from scipy.ndimage import zoom
from huey.contrib.djhuey import task
from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required

from ..utils import set_task_status, is_compressed, is_uuid
from ..models import FileSetModel
from ..data.datamanager import DataManager
from ..data.logmanager import LogManager
from .taskexception import TaskException
from .task import Task
from .taskmanager import TaskManager

LOG = LogManager()


class RescaleDicomTask(Task):
    def __init__(self) -> None:
        super(RescaleDicomTask, self).__init__(
            name='rescaledicomtask',
            display_name='Rescale DICOM to 512 x 512',
            description='This task rescales DICOM images to 512 x 512 such that they can be analysed by the Mosamatic AI model. If images are rectangular (columns unequal rows) the images will first be zero-padded along the short dimension to obtain a larger but square image. Then the image will be scaled back to 512 x 512 and its pixel spacing updated to reflect the changes',
            html_page='tasks/rescaledicomtask.html',
            url_pattern='/tasks/rescaledicomtask',
        )

    @staticmethod
    def rescale_image(f, data_manager: DataManager, fileset: FileSetModel, target_size: int) -> bool:
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
            pixel_array_rescaled = zoom(pixel_array_padded, zoom=(target_size / new_rows), order=3) # Cubic interpolation
            pixel_array_rescaled = pixel_array_rescaled.astype(pixel_array.dtype)
            original_pixel_spacing = p.PixelSpacing
            new_pixel_spacing = [ps * (new_rows / target_size) for ps in original_pixel_spacing]
            p.PixelSpacing = new_pixel_spacing
            p.PixelData = pixel_array_rescaled.tobytes()
            p.Rows = target_size
            p.Columns = target_size
            new_file_path = os.path.join(fileset.path, os.path.split(f.path)[1])
            p.save_as(new_file_path)
            data_manager.create_file(new_file_path, fileset)
            return True
        except pydicom.errors.InvalidDicomError:
            return False
        
    def run(self, task_status_id: str, fileset_id: str, output_fileset_name: str, user: User, target_size: int=512) -> bool:
        name = self.name
        LOG.info(f'name: {name}, task_status_id: {task_status_id}, fileset_id: {fileset_id}, output_fileset_name: {output_fileset_name}, target_size: {target_size}')
        data_manager = DataManager()
        if not is_uuid(fileset_id):
            raise TaskException('fileset_id is not UUID')
        fileset = data_manager.get_fileset(fileset_id)
        files = data_manager.get_files(fileset)
        new_fileset = data_manager.create_fileset(user, output_fileset_name)
        nr_steps = len(files)
        set_task_status(name, task_status_id, {'status': 'running', 'progress': 0})
        for step in range(nr_steps):
            if self.rescale_image(files[step], data_manager, new_fileset, target_size):
                progress = int(((step + 1) / (nr_steps)) * 100)
                set_task_status(name, task_status_id, {'status': 'running', 'progress': progress})
            else:
                LOG.warning(f'Could not rescale image {files[step].path}, skipping...')
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
                return task_manager.run_task_and_get_response(rescaledicomtask, fileset_id, output_fileset_name, request.user, 512)
            else:
                LOG.warning(f'no fileset ID selected')
                pass
        elif request.method == 'GET':
            response = task_manager.get_response('rescaledicomtask', request)
            if response:
                return response
        else:
            pass
        filesets = data_manager.get_filesets(request.user)
        task = data_manager.get_task_by_name('rescaledicomtask')
        return render(request, task.html_page, context={'filesets': filesets, 'task': task})
    

# https://chatgpt.com/c/66fa806e-1a08-800b-81dd-6fd260753341
@task()
def rescaledicomtask(task_status_id: str, fileset_id: str, output_fileset_name: str, user: User, target_size: int=512) -> bool:
    return RescaleDicomTask().run(task_status_id, fileset_id, output_fileset_name, user, target_size)