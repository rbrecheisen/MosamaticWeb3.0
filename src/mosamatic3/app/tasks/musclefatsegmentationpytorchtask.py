import os
import torch
import pydicom
import pydicom.errors
import zipfile
import json
import numpy as np

from typing import List, Any
from huey.contrib.djhuey import task
from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required

from .taskexception import TaskException
from ..utils import set_task_status, normalize_between, is_compressed, \
    get_pixels_from_dicom_object, convert_labels_to_157, is_uuid, AlbertaColorMap
from ..data.datamanager import DataManager
from ..data.logmanager import LogManager
from ..data.pngimagegenerator import PngImageGenerator
from .task import Task
from .taskmanager import TaskManager
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
            visible=True, installed=False,
        )

    @staticmethod
    def load_model_files(files: List[FileModel]) -> List[Any]:
        for f in files:
            if f.name.startswith('model'):
                model = torch.load(f.path)
            elif f.name.startswith('contour_model'):
                contour_model = torch.load(f.path)
            elif f.name == 'params.json':
                with open(f.path, 'r') as obj:
                    parameters = json.load(obj)
            else:
                pass
        return [model, contour_model, parameters]
    
    def run(self, task_status_id: str, fileset_id: str, model_fileset_id: str, output_fileset_name: str, user :User) -> bool:
        LOG.info(f'name: {self.name}, task_status_id: {task_status_id}, fileset_id: {fileset_id}, model_fileset_id: {model_fileset_id}, output_fileset_name: {output_fileset_name}')
        LOG.info(f'GPU available: {torch.cuda.is_available()}')
        return True
        
    @staticmethod
    @login_required
    def view(request: HttpRequest) -> HttpResponse:
        data_manager = DataManager()
        task_manager = TaskManager()
        if request.method == 'POST':
            fileset_id = request.POST.get('fileset_id', None)
            if fileset_id:
                model_fileset_id = request.POST.get('model_fileset_id', None)
                if model_fileset_id:
                    output_fileset_name = request.POST.get('output_fileset_name', None)
                    return task_manager.run_task_and_get_response(musclefatsegmentationpytorchtask, fileset_id, model_fileset_id, output_fileset_name, request.user)
                else:
                    LOG.warning(f'no model fileset ID selected')
            else:
                LOG.warning(f'no fileset ID selected')
        elif request.method == 'GET':
            response = task_manager.get_response('musclefatsegmentationpytorchtask', request)
            if response:
                return response
        else:
            pass
        filesets = data_manager.get_filesets(request.user)
        task = data_manager.get_task_by_name('musclefatsegmentationpytorchtask')
        return render(request, task.html_page, context={'filesets': filesets, 'task': task})

@task()
def musclefatsegmentationpytorchtask(task_status_id: str, fileset_id: str, model_fileset_id: str, output_fileset_name: str, user :User) -> bool:
    return MuscleFatSegmentationPyTorchTask().run(task_status_id, fileset_id, model_fileset_id, output_fileset_name, user)