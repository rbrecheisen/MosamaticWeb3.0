import json
import pydicom
import pydicom.errors

from typing import Dict
from huey.contrib.djhuey import task
from django.contrib.auth.models import User
from ..utils import is_uuid, set_task_status
from ..data.datamanager import DataManager
from ..data.logmanager import LogManager
from .taskexception import TaskException

LOG = LogManager()

"""
What do we want as output of this task? An HTML page that reports:
(1) Modalities
(2) 
"""


class DicomSeries:
    def __init__(self, modality: str) -> None:
        self.modality = modality
        self.images = {}

    def add_image(self, p: pydicom.FileDataset) -> None:
        if p.SOPInstanceUID not in self.images.keys():
            self.images[p.SOPInstanceUID] = p

    def nr_images(self) -> int:
        return len(self.images.keys())
    
    def __str__(self) -> str:
        return f'DicomSeries[{self.modality}], images: {self.nr_images()}'


def load_dicom_image(file_path: str) -> pydicom.FileDataset:
    try:
        return pydicom.dcmread(file_path, stop_before_pixels=True)
    except pydicom.errors.InvalidDicomError:
        return None


@task()
def dicomstructuretask(task_status_id: str, fileset_id: str, output_fileset_name: str, user :User) -> bool:
    name = 'dicomstructuretask'
    LOG.info(f'name: {name}, task_status_id: {task_status_id}, fileset_id: {fileset_id}, output_fileset_name: {output_fileset_name}')
    data_manager = DataManager()
    if not is_uuid(fileset_id):
        raise TaskException(f'{name}() fileset_id is not UUID')
    fileset = data_manager.get_fileset(fileset_id)
    files = data_manager.get_files(fileset)
    nr_steps = len(files)
    dicom_series_list = {}
    set_task_status(name, task_status_id, {'status': 'running', 'progress': 0})
    for step in range(nr_steps):

        # Analyze files
        dicom_image = load_dicom_image(files[step].path)
        if dicom_image:
            series_instance_uid = dicom_image.SeriesInstanceUID
            if series_instance_uid not in dicom_series_list.keys():
                dicom_series_list[dicom_image.SeriesInstanceUID] = DicomSeries(dicom_image.Modality)
            dicom_series_list[dicom_image.SeriesInstanceUID].add_image(dicom_image)

        progress = int(((step + 1) / (nr_steps)) * 100)
        set_task_status(name, task_status_id, {'status': 'running', 'progress': progress})
    for k, v in dicom_series_list.items():
        LOG.info(str(v))
    set_task_status(name, task_status_id, {'status': 'completed', 'progress': 100})
    return True