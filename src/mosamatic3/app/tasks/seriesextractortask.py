import os
import json
import pydicom
import pydicom.errors
import numpy as np

from typing import Dict, List
from scipy.ndimage import zoom
from huey.contrib.djhuey import task
from django.contrib.auth.models import User

from ..utils import set_task_status, is_compressed, is_uuid
from ..models import FileSetModel, FileModel
from ..data.datamanager import DataManager
from ..data.logmanager import LogManager
from ..data.seriesextractors import (
    SeriesExtractor,
    CtSeriesExtractor,
    MrSeriesExtractor,
    DixonInPhaseSeriesExtractor,
    DixonOppositePhaseSeriesExtractor,
    DixonWaterSeriesExtractor,
    DwiAdcSeriesExtractor,
    DwiBValSeriesExtractor,
)
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
            parameter_names=['fileset_id', 'image_type'],
            visible=True,
        )

    def get_extractor(self, image_type: str, fileset: FileSetModel) -> SeriesExtractor:
        if image_type == 'CT':
            return CtSeriesExtractor(fileset.file_paths)
        if image_type == 'IN_PHASE':
            return DixonInPhaseSeriesExtractor(fileset.file_paths)
        if image_type == 'OPP_PHASE':
            return DixonOppositePhaseSeriesExtractor(fileset.file_paths)
        if image_type == 'WATER':
            return DixonWaterSeriesExtractor(fileset.file_paths)
        if image_type == 'ADC':
            return DwiAdcSeriesExtractor(fileset.file_paths)
        if image_type == 'CALC_BVALUE':
            return DwiBValSeriesExtractor(fileset.file_paths)
        return None

    def run(self, task_status_id: str, fileset_id: str, image_type: str, user: User) -> bool:
        name = self.name
        LOG.info(f'name: {name}, task_status_id: {task_status_id}, fileset_id: {fileset_id}, image_type: {image_type}')
        data_manager = DataManager()
        if not is_uuid(fileset_id):
            raise TaskException('fileset_id is not UUID')
        fileset = data_manager.get_fileset(fileset_id)
        extractor = self.get_extractor(image_type, fileset)
        set_task_status(name, task_status_id, {'status': 'running', 'progress': 0})
        if extractor:
            series = extractor.run()
            for modality in series.keys():
                for patient_id in series[modality].keys():
                    for series_instance_uid in series[modality][patient_id].keys():
                        files = series[modality][patient_id][series_instance_uid]
                        fileset = data_manager.create_fileset(user, f'{fileset.name}_{modality}_{patient_id}_{image_type}')
                        for f in files:
                            data_manager.create_file(f, fileset)
        else:
            LOG.error(f'Could not find series extractor for image type {image_type}')
        set_task_status(name, task_status_id, {'status': 'completed', 'progress': 100})
        return True
    

@task()
def seriesextractortask(task_status_id: str, task_parameters: Dict[str, str]) -> bool:
    return SeriesExtractorTask().run(
        task_status_id, 
        task_parameters['fileset_id'], 
        task_parameters['image_type'],
        task_parameters['user'],
    )