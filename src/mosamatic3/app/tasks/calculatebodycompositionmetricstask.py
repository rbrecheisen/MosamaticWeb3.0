import os
import pydicom
import pydicom.errors
import numpy as np

from typing import List, Any
from huey.contrib.djhuey import task
from django.conf import settings
from django.contrib.auth.models import User
from .taskexception import TaskException
from ..utils import set_task_progress, delete_task_progress, normalize_between, is_compressed, get_pixels_from_dicom_object, convert_labels_to_157
from ..data.datamanager import DataManager
from ..data.logmanager import LogManager
from ..models import FileModel

LOG = LogManager()


@task()
def calculatebodycompositionmetricstask(task_progress_id: str, fileset_id: str, segmentation_fileset_id: str, output_fileset_name: str, user :User) -> bool:
    name = 'calculatebodycompositionmetricstask'
    LOG.info(f'name: {name}, task_progress_id: {task_progress_id}, fileset_id: {fileset_id}, segmentation_fileset_id: {segmentation_fileset_id}, output_fileset_name: {output_fileset_name}')
    data_manager = DataManager()
    try:
        fileset = data_manager.get_fileset(fileset_id)
        if fileset is None:
            raise TaskException('musclefatsegmentationtask() fileset is None')
        segmentation_fileset = data_manager.get_fileset(segmentation_fileset_id)
        if segmentation_fileset is None:
            raise TaskException('musclefatsegmentationtask() segmentation_fileset is None')
        output_fileset = data_manager.create_fileset(user, output_fileset_name)
        files = data_manager.get_files(fileset)
        segmentation_files = data_manager.get_files(segmentation_fileset)
        nr_steps = len(files)
        set_task_progress(name, task_progress_id, 0)
        for step in range(nr_steps):
            pass
    except TaskException as e:
        LOG.error(f'musclefatsegmentation() exception occurred while processing files ({e})')