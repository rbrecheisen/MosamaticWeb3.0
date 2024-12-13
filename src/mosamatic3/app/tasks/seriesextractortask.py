import os
import pydicom
import pydicom.errors
import numpy as np

from typing import Dict
from scipy.ndimage import zoom
from huey.contrib.djhuey import task
from django.contrib.auth.models import User

from ..utils import set_task_status, is_compressed, is_uuid
from ..models import FileSetModel
from ..data.datamanager import DataManager
from ..data.logmanager import LogManager
from .taskexception import TaskException
from .task import Task

LOG = LogManager()


class SeriesExtractorTask(Task):
    def __init__(self) -> None:
        super(SeriesExtractorTask, self).__init__(
            name='seriesextractortask',
            display_name='Extract Series From FileSet',
            description='Extracts specific DICOM series from a fileset and creates new filesets for each series',
            html_page='tasks/seriesextractortask.html',
            url_pattern='/tasks/seriesextractortask',
            task_func=seriesextractortask,
            parameter_names=['fileset_id', 'image_type', 'output_fileset_name_prefix'],
            visible=True,
        )

    def run(self, task_status_id: str, fileset_id: str, output_fileset_name_prefix: str, image_type: str, user: User) -> bool:
        name = self.name
        LOG.info(f'name: {name}, task_status_id: {task_status_id}, fileset_id: {fileset_id}, image_type: {image_type}, output_fileset_name_prefix: {output_fileset_name_prefix}')
        data_manager = DataManager()
        if not is_uuid(fileset_id):
            raise TaskException('fileset_id is not UUID')
        fileset = data_manager.get_fileset(fileset_id)
        files = data_manager.get_files(fileset)
        # new_fileset = data_manager.create_fileset(user, output_fileset_name)
        nr_steps = len(files)
        set_task_status(name, task_status_id, {'status': 'running', 'progress': 0})
        for step in range(nr_steps):
            # Do your stuff
            progress = int(((step + 1) / (nr_steps)) * 100)
            set_task_status(name, task_status_id, {'status': 'running', 'progress': progress})
        set_task_status(name, task_status_id, {'status': 'completed', 'progress': 100})
        return True
    

@task()
def seriesextractortask(task_status_id: str, task_parameters: Dict[str, str]) -> bool:
    return SeriesExtractorTask().run(
        task_status_id, 
        task_parameters['fileset_id'], 
        task_parameters['image_type'],
        task_parameters['output_fileset_name_prefix'], 
        task_parameters['user'],
    )