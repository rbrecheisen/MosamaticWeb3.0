import os
import pydicom
import pydicom.errors
import numpy as np
import pandas as pd

from typing import List, Dict, Union
from huey.contrib.djhuey import task
from django.contrib.auth.models import User
from .taskexception import TaskException
from ..utils import set_task_progress, delete_task_progress, set_task_status, is_compressed, get_pixels_from_dicom_object, \
    is_uuid, convert_numpy_array_to_png_image, AlbertaColorMap
from ..data.datamanager import DataManager
from ..data.logmanager import LogManager
from ..models import FileModel

LOG = LogManager()


def get_segmentation_file_for_dicom_file(segmentation_files: List[FileModel], dicom_file: FileModel) -> FileModel:
    for segmentation_file in segmentation_files:
        if dicom_file.name + '.seg.npy' == segmentation_file.name:
            return segmentation_file
    return None


def load_dicom_file(f: FileModel) -> Union[np.ndarray, List[float]]:
    try:
        p = pydicom.dcmread(f.path)
        if is_compressed(p):
            p.decompress()
        pixels = get_pixels_from_dicom_object(p, normalize=True)
        return pixels, p.PixelSpacing
    except pydicom.errors.InvalidDicomError:
        return None, None


def load_segmentation_file(f: FileModel):
    return np.load(f.path)


def load_patient_heights(df: pd.DataFrame) -> Dict[str, float]:
        data = {}
        for _, row in df.iterrows():
            data[row['file']] = float(row['height'])
        return data


def output_metrics_to_string(output_metrics: Dict[str, float]) -> str:
    text = ''
    for metric, value in output_metrics.items():
        text += f'  - {metric}: {value}\n'
    return text


@task()
def segmentationpngtask(task_status_id: str, segmentation_fileset_id: str, output_fileset_name: str, user :User) -> bool:
    name = 'segmentationpngtask'
    LOG.info(f'name: {name}, task_status_id: {task_status_id}, segmentation_fileset_id: {segmentation_fileset_id}, output_fileset_name: {output_fileset_name}')
    data_manager = DataManager()
    try:
        if not is_uuid(segmentation_fileset_id):
            raise TaskException('segmentationpngtask() segmentation_fileset_id is not UUID')
        segmentation_fileset = data_manager.get_fileset(segmentation_fileset_id)
        if segmentation_fileset is None:
            raise TaskException('segmentationpngtask() segmentation_fileset is None')
        segmentation_files = data_manager.get_files(segmentation_fileset)
        nr_steps = len(segmentation_files)
        set_task_status(name, task_status_id, {'status': 'running', 'progress': 0})
        output_fileset = data_manager.create_fileset(user, output_fileset_name)
        for step in range(nr_steps):
            segmentation_file = segmentation_files[step]
            numpy_array = np.load(segmentation_file.path)
            png_file_name = os.path.split(segmentation_file.path)[1] + '.png'
            png_file_path = convert_numpy_array_to_png_image(
                numpy_array_file_path_or_object=numpy_array, 
                color_map=AlbertaColorMap(),
                output_dir_path=output_fileset.path,
                png_file_name=png_file_name,
            )
            data_manager.create_file(png_file_path, output_fileset)
            LOG.info(f'{segmentation_file.path} created {png_file_name}')
            progress = int(((step + 1) / (nr_steps)) * 100)
            set_task_status(name, task_status_id, {'status': 'running', 'progress': progress})
        set_task_status(name, task_status_id, {'status': 'completed', 'progress': 100})
        return True
    except TaskException as e:
        LOG.error(f'segmentationpngtask() exception occurred while processing files ({e})')
        set_task_status(name, task_status_id, {'status': 'failed', 'progress': -1})
        return False