import os
import torch
import pydicom
import pydicom.errors
import json
import numpy as np

from typing import List, Any, Dict
from huey.contrib.djhuey import task
from django.contrib.auth.models import User

from .taskexception import TaskException
from ..utils import set_task_status, normalize_between, is_compressed, \
    get_pixels_from_dicom_object, convert_labels_to_157, is_uuid, AlbertaColorMap
from ..data.datamanager import DataManager
from ..data.logmanager import LogManager
from ..data.pngimagegenerator import PngImageGenerator
from .task import Task
from ..models import FileModel

LOG = LogManager()


class MuscleFatSegmentationPyTorchTask(Task):
    def __init__(self) -> None:
        super(MuscleFatSegmentationPyTorchTask, self).__init__(
            name='musclefatsegmentationpytorchtask',
            display_name='Muscle and fat segmentation (PyTorch)',
            description='This task runs muscle and fat segmentation on DICOM images acquired at the 3rd lumbar vertebral level (L3).',
            html_page='tasks/musclefatsegmentationpytorchtask.html',
            url_pattern='/tasks/musclefatsegmentationpytorchtask',
            task_func=musclefatsegmentationpytorchtask,
            parameter_names=['fileset_id', 'model_fileset_id', 'output_fileset_name'],
            visible=True,
        )

    @staticmethod
    def load_model_files(files: List[FileModel]) -> List[Any]:
        for f in files:
            if f.name.startswith('model'):
                model = torch.load(f.path)
                model.to('cpu')
                model.eval()
            elif f.name.startswith('contour_model'):
                contour_model = torch.load(f.path)
                contour_model.to('cpu')
                contour_model.eval()
            elif f.name == 'params.json':
                with open(f.path, 'r') as obj:
                    parameters = json.load(obj)
            else:
                pass
        return [model, contour_model, parameters]
    
    @staticmethod
    def predict_contour(contour_model, source_image, parameters) -> np.array:
        ct = np.copy(source_image)
        ct = normalize_between(ct, parameters['min_bound_contour'], parameters['max_bound_contour'])
        img2 = np.expand_dims(ct, 0)
        img2 = np.expand_dims(img2, -1)
        img2_tensor = torch.tensor(img2, dtype=torch.float32).unsqueeze(0).unsqueeze(0).to('cpu')
        with torch.no_grad():
            pred = contour_model(img2_tensor).cpu().numpy()
        # pred = contour_model.predict([img2])
        pred_squeeze = np.squeeze(pred)
        pred_max = pred_squeeze.argmax(axis=-1)
        mask = np.uint8(pred_max)
        return mask

    def process_file(self, f: FileModel, output_fileset_path: str, model, contour_model, parameters, mode='argmax') -> bool:
        try:
            p = pydicom.dcmread(f.path)
            if is_compressed(p):
                p.decompress()
            if p.Rows != 512 or p.Columns != 512:
                LOG.warning(f'wrong dimensions: {p.Rows} x {p.Columns} (should be 512 x 512)')
                return None
            img1 = get_pixels_from_dicom_object(p, normalize=True)
            # img1_tensor = torch.tensor(img1, dtype=torch.float32).unsqueeze(0).unsqueeze(0).to('cpu')
            if contour_model:
                mask = self.predict_contour(contour_model, img1, parameters)
                img1 = normalize_between(img1, parameters['min_bound'], parameters['max_bound'])
                img1 = img1 * mask
            else:
                img1 = normalize_between(img1, parameters['min_bound'], parameters['max_bound'])
            img1 = img1.astype(np.float32)
            img2 = np.expand_dims(img1, 0)
            img2 = np.expand_dims(img2, -1)
            img2_tensor = torch.tensor(img2, dtype=torch.float32).unsqueeze(0).unsqueeze(0).to('cpu')
            with torch.no_grad():
                pred = model(img2_tensor).cpu().numpy()
            # pred = model.predict([img2])
            pred_squeeze = np.squeeze(pred)
            segmentation_file_path = None
            if mode == 'argmax':
                pred_max = pred_squeeze.argmax(axis=-1)
                pred_max = convert_labels_to_157(pred_max)
                segmentation_file_path = os.path.join(output_fileset_path, f'{f.name}.seg.npy')
                np.save(segmentation_file_path, pred_max)
            elif mode == 'probabilities':
                LOG.warning(f'probabilities not implemented yet')
            segmentation_png_file_path = PngImageGenerator().run(segmentation_file_path, color_map=AlbertaColorMap())
            return segmentation_file_path, segmentation_png_file_path
        except pydicom.errors.InvalidDicomError:
            return None, None

    def run(self, task_status_id: str, fileset_id: str, model_fileset_id: str, output_fileset_name: str, user :User) -> bool:
        LOG.info(f'name: {self.name}, task_status_id: {task_status_id}, fileset_id: {fileset_id}, model_fileset_id: {model_fileset_id}, output_fileset_name: {output_fileset_name}')
        data_manager = DataManager()
        try:
            if not is_uuid(fileset_id):
                raise TaskException('fileset_id is not UUID')
            fileset = data_manager.get_fileset(fileset_id)
            if fileset is None:
                raise TaskException('fileset is None')
            if not is_uuid(model_fileset_id):
                raise TaskException('model_fileset_id is not UUID')
            model_fileset = data_manager.get_fileset(model_fileset_id)
            if model_fileset is None:
                raise TaskException('model_fileset is None')
            output_fileset = data_manager.create_fileset(user, output_fileset_name)
            output_png_fileset = data_manager.create_fileset(user, output_fileset_name + '_png')
            files = data_manager.get_files(fileset)
            model_files = data_manager.get_files(model_fileset)
            segmentation_file_paths, segmentation_png_file_paths = [], []
            nr_steps = len(files)
            model, contour_model, parameters = self.load_model_files(files=model_files)
            if model is None or parameters is None:
                raise TaskException('model or parameters are None')
            if model and parameters:
                set_task_status(self.name, task_status_id, {'status': 'running', 'progress': 0})
                for step in range(nr_steps):
                    segmentation_file_path, segmentation_png_file_path = self.process_file(files[step], output_fileset.path, model, contour_model, parameters) # skipping "mode=argmax"
                    if segmentation_file_path:
                        segmentation_file_paths.append(segmentation_file_path)
                        segmentation_png_file_paths.append(segmentation_png_file_path)
                        LOG.info(f'processed file {files[step].path}')
                    else:
                        LOG.warning(f'could not process file {files[step].path}')
                    progress = int(((step + 1) / (nr_steps)) * 100)
                    set_task_status(self.name, task_status_id, {'status': 'running', 'progress': progress})
            else:
                LOG.error(f'model and/or parameters are None')
            # for f in segmentation_file_paths:
            for i in range(len(segmentation_file_paths)):
                data_manager.create_file(segmentation_png_file_paths[i], output_png_fileset)
                f = data_manager.create_file(segmentation_file_paths[i], output_fileset)
                # Also set png_path of File object so we can create <a href=""> item in the fileset.html page
                f.png_path = segmentation_png_file_paths[i]
                f.save()
            set_task_status(self.name, task_status_id, {'status': 'completed', 'progress': 100})
            return True
        except TaskException as e:
            LOG.error(f'exception occurred while processing files ({e})')
            set_task_status(self.name, task_status_id, {'status': 'failed', 'progress': -1})
            return False
        

@task()
def musclefatsegmentationpytorchtask(task_status_id: str, task_parameters: Dict[str, str]) -> bool:
    return MuscleFatSegmentationPyTorchTask().run(
        task_status_id, 
        task_parameters['fileset_id'], 
        task_parameters['model_fileset_id'], 
        task_parameters['output_fileset_name'], 
        task_parameters['user']
    )