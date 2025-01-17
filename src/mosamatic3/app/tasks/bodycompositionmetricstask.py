import os
import json
import pydicom
import pydicom.errors
import numpy as np
import pandas as pd

from typing import List, Dict, Union
from huey.contrib.djhuey import task
from django.contrib.auth.models import User

from .taskexception import TaskException
from ..utils import set_task_status, is_compressed, get_pixels_from_dicom_object, \
    calculate_area, calculate_index, calculate_mean_radiation_attenuation, create_name_with_timestamp, is_uuid
from ..data.datamanager import DataManager
from ..data.logmanager import LogManager
from ..models import FileModel
from ..tasks.task import Task

LOG = LogManager()

MUSCLE = 1
VAT = 5
SAT = 7


class BodyCompositionMetricsTask(Task):
    def __init__(self) -> None:
        super(BodyCompositionMetricsTask, self).__init__(
            name='bodycompositionmetricstask',
            display_name='Body composition metrics',
            description='This task calculates body composition metrics from L3 images and corresponding muscle and fat segmentations',
            html_page='tasks/bodycompositionmetricstask.html',
            url_pattern='/tasks/bodycompositionmetricstask',
            task_func=bodycompositionmetricstask,
            parameter_names=['fileset_id', 'segmentation_fileset_id', 'output_fileset_name', 'patient_heights_fileset_id'],
            visible=True,
        )

    @staticmethod
    def get_segmentation_file_for_dicom_file(segmentation_files: List[FileModel], dicom_file: FileModel) -> FileModel:
        for segmentation_file in segmentation_files:
            if dicom_file.name + '.seg.npy' == segmentation_file.name:
                return segmentation_file
        return None

    def load_dicom_file(self, f: FileModel) -> Union[np.ndarray, List[float]]:
        try:
            p = pydicom.dcmread(f.path)
            if is_compressed(p):
                p.decompress()
            pixels = get_pixels_from_dicom_object(p, normalize=True)
            return pixels, p.PixelSpacing
        except pydicom.errors.InvalidDicomError:
            return None, None

    @staticmethod
    def load_segmentation_file(f: FileModel):
        return np.load(f.path)

    @staticmethod
    def load_patient_heights(df: pd.DataFrame) -> Dict[str, float]:
            data = {}
            for _, row in df.iterrows():
                data[row['file']] = float(row['height'])
            return data

    @staticmethod
    def output_metrics_to_string(output_metrics: Dict[str, float]) -> str:
        text = ''
        for metric, value in output_metrics.items():
            text += f'  - {metric}: {value}\n'
        return text
    
    def run(self, task_status_id: str, fileset_id: str, segmentation_fileset_id: str, patient_heights_fileset_id: str, output_fileset_name: str, user :User) -> bool:
        self.name = 'bodycompositionmetricstask'
        LOG.info(f'name: {self.name}, task_status_id: {task_status_id}, fileset_id: {fileset_id}, segmentation_fileset_id: {segmentation_fileset_id}, patient_heights_fileset_id: {patient_heights_fileset_id}, output_fileset_name: {output_fileset_name}')
        data_manager = DataManager()
        try:
            if not is_uuid(fileset_id):
                raise TaskException(f'fileset_id is not UUID')
            fileset = data_manager.get_fileset(fileset_id)
            if fileset is None:
                raise TaskException(f'fileset is None')
            if not is_uuid(segmentation_fileset_id):
                raise TaskException(f'segmentation_fileset_id is not UUID')
            segmentation_fileset = data_manager.get_fileset(segmentation_fileset_id)
            if segmentation_fileset is None:
                raise TaskException(f'segmentation_fileset is None')
            patient_heights = None
            if patient_heights_fileset_id and is_uuid(patient_heights_fileset_id):
                patient_heights_fileset = data_manager.get_fileset(patient_heights_fileset_id)
                if patient_heights_fileset is None:
                    raise TaskException(f'patient_heights_fileset is None')
                else:
                    patient_heights_file = data_manager.get_files(patient_heights_fileset)[0]
                    patient_heights_dataframe = pd.read_csv(patient_heights_file.path, sep='[,;]+', dtype=str)
                    patient_heights = self.load_patient_heights(patient_heights_dataframe)
                    LOG.info(json.dumps(patient_heights, indent=4))
            files = data_manager.get_files(fileset)
            segmentation_files = data_manager.get_files(segmentation_fileset)
            nr_steps = len(files)
            output_metrics = {}
            set_task_status(self.name, task_status_id, {'status': 'running', 'progress': 0})
            for step in range(nr_steps):
                dicom_file = files[step]
                segmentation_file = self.get_segmentation_file_for_dicom_file(segmentation_files, dicom_file)
                if segmentation_file:
                    image, pixel_spacing = self.load_dicom_file(dicom_file)
                    segmentation = self.load_segmentation_file(segmentation_file)
                    # Calculate metrics for predicted segmentation
                    output_metrics[dicom_file] = {}
                    output_metrics[dicom_file]['file'] = dicom_file.name
                    output_metrics[dicom_file]['muscle_area_pred'] = calculate_area(segmentation, MUSCLE, pixel_spacing)
                    if patient_heights:
                        if dicom_file.name in patient_heights.keys():
                            output_metrics[dicom_file]['muscle_index_pred'] = calculate_index(
                                area=output_metrics[dicom_file]['muscle_area_pred'], height=patient_heights[dicom_file.name])
                        else:
                            output_metrics[dicom_file]['muscle_index_pred'] = 0
                    output_metrics[dicom_file]['vat_area_pred'] = calculate_area(segmentation, VAT, pixel_spacing)
                    if patient_heights:
                        if dicom_file.name in patient_heights.keys():
                            output_metrics[dicom_file]['vat_index_pred'] = calculate_index(
                                area=output_metrics[dicom_file]['vat_area_pred'], height=patient_heights[dicom_file.name])
                        else:
                            output_metrics[dicom_file]['vat_index_pred'] = 0
                    output_metrics[dicom_file]['sat_area_pred'] = calculate_area(segmentation, SAT, pixel_spacing)
                    if patient_heights:
                        if dicom_file.name in patient_heights.keys():
                            output_metrics[dicom_file]['sat_index_pred'] = calculate_index(
                                area=output_metrics[dicom_file]['sat_area_pred'], height=patient_heights[dicom_file.name])
                        else:
                            output_metrics[dicom_file]['sat_index_pred'] = 0
                    output_metrics[dicom_file]['muscle_ra_pred'] = calculate_mean_radiation_attenuation(image, segmentation, MUSCLE)
                    output_metrics[dicom_file]['vat_ra_pred'] = calculate_mean_radiation_attenuation(image, segmentation, VAT)
                    output_metrics[dicom_file]['sat_ra_pred'] = calculate_mean_radiation_attenuation(image, segmentation, SAT)
                    LOG.info(self.output_metrics_to_string(output_metrics[dicom_file]))
                    # Update progress
                    progress = int(((step + 1) / (nr_steps)) * 100)
                    set_task_status(self.name, task_status_id, {'status': 'running', 'progress': progress})
            # Create output fileset
            output_fileset = data_manager.create_fileset(user, output_fileset_name)
            first_key = next(iter(output_metrics))
            columns = list(output_metrics[first_key].keys())
            data = {}
            for column in columns:
                data[column] = []
            for file_path in output_metrics.keys():
                for column in columns:
                    data[column].append(output_metrics[file_path][column])
            csv_file_path = os.path.join(output_fileset.path, create_name_with_timestamp('scores') + '.csv')
            df = pd.DataFrame(data=data)
            df.to_csv(csv_file_path, index=False)
            data_manager.create_file(csv_file_path, output_fileset)
            set_task_status(self.name, task_status_id, {'status': 'completed', 'progress': 100})
            return True
        except TaskException as e:
            LOG.error(f'exception occurred while processing files ({e})')
            set_task_status(self.name, task_status_id, {'status': 'failed', 'progress': -1})
            return False
    

@task()
def bodycompositionmetricstask(task_status_id: str, task_parameters: Dict[str, str]) -> bool:
    return BodyCompositionMetricsTask().run(
        task_status_id, 
        task_parameters['fileset_id'], 
        task_parameters['segmentation_fileset_id'], 
        task_parameters['patient_heights_fileset_id'], 
        task_parameters['output_fileset_name'], 
        task_parameters['user'],
    )