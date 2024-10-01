import os
import pydicom
import pydicom.errors
import zipfile
import json
import numpy as np

from typing import List, Any
from huey.contrib.djhuey import task
from django.conf import settings
from django.contrib.auth.models import User
from ..utils import set_task_progress, delete_task_progress, normalize_between, is_compressed, get_pixels_from_dicom_object, convert_labels_to_157
from ..data.datamanager import DataManager
from ..data.logmanager import LogManager
from ..models import FileModel

LOG = LogManager()


class TensorFlowModel:
    def __init__(self) -> None:
        self.model = None

    def load(self, model_file_path: str) -> None:
        import tensorflow as tf
        try:
            self.model = tf.keras.models.load_model(model_file_path, compile=False)
        except:
            LOG.error(f'TensorFlowModel.load() could not load model')

    def predict(self, input: np.array) -> np.array:
        if self.model:
            return self.model.predict(input)
        LOG.error(f'TensorFlowModel.predict() model not loaded yet')
        return None


def load_model_files(files: List[FileModel]) -> List[Any]:
    tf_loaded = False
    for f in files:
        if f.name == 'model.zip':
            if not tf_loaded:
                import tensorflow as tf # Only load TensorFlow package if necessary (takes some time)
                tf_loaded = True
            tf_model_dir = settings.DATA_DIR_TF_MODEL
            LOG.info(f'tf_model_dir: {tf_model_dir}')
            with zipfile.ZipFile(f.path) as zipObj:
                zipObj.extractall(path=tf_model_dir)
            tf_model = TensorFlowModel()
            tf_model.load(model_file_path=tf_model_dir)
        elif f.name == 'contour_model.zip':
            if not tf_loaded:
                import tensorflow as tf # Only load TensorFlow package if necessary (takes some time)
                tf_loaded = True
            tf_model_dir = settings.DATA_DIR_TF_MODEL
            with zipfile.ZipFile(f.path) as zipObj:
                zipObj.extractall(path=tf_model_dir)
            tf_contour_model = TensorFlowModel()
            tf_contour_model.load(model_file_path=tf_model_dir)
        elif f.name == 'params.json':
            with open(f.path, 'r') as obj:
                parameters = json.load(obj)
        else:
            pass
    return [tf_model, tf_contour_model, parameters]


def predict_contour(contour_model, source_image, parameters) -> np.array:
    ct = np.copy(source_image)
    ct = normalize_between(ct, parameters['min_bound_contour'], parameters['max_bound_contour'])
    img2 = np.expand_dims(ct, 0)
    img2 = np.expand_dims(img2, -1)
    pred = contour_model.predict([img2])
    pred_squeeze = np.squeeze(pred)
    pred_max = pred_squeeze.argmax(axis=-1)
    mask = np.uint8(pred_max)
    return mask


def process_file(f: FileModel, output_fileset_path: str, model, contour_model, parameters, mode='argmax') -> bool:
    try:
        p = pydicom.dcmread(f.path)
        if is_compressed(p):
            p.decompress()
        img1 = get_pixels_from_dicom_object(p, normalize=True)
        if contour_model:
            mask = predict_contour(contour_model, img1, parameters)
            img1 = normalize_between(img1, parameters['min_bound'], parameters['max_bound'])
            img1 = img1 * mask
        else:
            img1 = normalize_between(img1, parameters['min_bound'], parameters['max_bound'])
        img1 = img1.astype(np.float32)
        img2 = np.expand_dims(img1, 0)
        img2 = np.expand_dims(img2, -1)
        pred = model.predict([img2])
        pred_squeeze = np.squeeze(pred)
        segmentation_file_path = None
        if mode == 'argmax':
            pred_max = pred_squeeze.argmax(axis=-1)
            pred_max = convert_labels_to_157(pred_max)
            segmentation_file_path = os.path.join(output_fileset_path, f'{f.name}.seg.npy')
            np.save(segmentation_file_path, pred_max)
        elif mode == 'probabilities':
            LOG.warning(f'musclefatsegmentationtask.process_file() probabilities not implemented yet')
        return segmentation_file_path
    except pydicom.errors.InvalidDicomError:
        return None


# @task()
def musclefatsegmentationtask(task_progress_id: str, fileset_id: str, model_fileset_id: str, output_fileset_name: str, user :User) -> bool:
    name = 'musclefatsegmentationtask'
    LOG.info(f'name: {name}, task_progress_id: {task_progress_id}, fileset_id: {fileset_id}, model_fileset_id: {model_fileset_id}, output_fileset_name: {output_fileset_name}')
    data_manager = DataManager()
    fileset = data_manager.get_fileset(fileset_id)
    model_fileset = data_manager.get_fileset(model_fileset_id)
    output_fileset = data_manager.create_fileset(user, output_fileset_name)
    files = data_manager.get_files(fileset)
    model_files = data_manager.get_files(model_fileset)
    segmentation_file_paths = []
    nr_steps = len(files)
    model, contour_model, parameters = load_model_files(files=model_files)
    if model and parameters:
        set_task_progress(name, task_progress_id, 0)
        for step in range(nr_steps):
            segmentation_file_path = process_file(files[step], output_fileset.path, model, contour_model, parameters) # skipping "mode=argmax"
            if segmentation_file_path:
                segmentation_file_paths.append(segmentation_file_path)
            progress = int(((step + 1) / (nr_steps)) * 100)
            set_task_progress(name, task_progress_id, progress)
            LOG.info(f'musclefatsegmentationtask() processed file {files[step].path}')
    else:
        LOG.error(f'musclefatsegmentationtask() model and/or parameters are None')
    for f in segmentation_file_paths:
        data_manager.create_file(f, output_fileset)
    delete_task_progress(name, task_progress_id)
    return True