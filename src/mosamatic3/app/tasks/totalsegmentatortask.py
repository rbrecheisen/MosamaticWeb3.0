import pydicom
import pydicom.errors

from typing import List, Dict
from huey.contrib.djhuey import task
from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required
from .taskexception import TaskException

from ..utils import set_task_status, is_uuid
from ..data.datamanager import DataManager
from ..data.logmanager import LogManager
from .task import Task
from .taskmanager import TaskManager
from ..models import FileModel, FileSetModel

LOG = LogManager()


class TotalSegmentatorTask(Task):
    def __init__(self) -> None:
        super(TotalSegmentatorTask, self).__init__(
            name='totalsegmentatortask',
            display_name='Total Segmentator task',
            description='This task runs Total Segmentator on a single CT or MRI scan',
            html_page='tasks/totalsegmentator.html',
            url_pattern='/tasks/totalsegmentator/',
            visible=False,
        )

    @staticmethod
    def find_series_in_fileset(fileset: FileSetModel, data_manager: DataManager) -> Dict[str, FileModel]:
        series_list = {}
        files = data_manager.get_files(fileset)
        for f in files:
            p = pydicom.dcmread(f.path, stop_before_pixels=True)
            if p.SeriesInstanceUID not in series_list.keys():
                series_list[p.SeriesInstanceUID] = []
            series_list[p.SeriesInstanceUID].append(f)
        return series_list

    @staticmethod
    def run_totalsegmentator_on_series(series_instance_uid: str, series_files: List[FileModel], mask_name: str) -> bool:
        """ What should this function do? It runs TS on a single CT series and outputs 100+ segmentations, each 
        a different NIFTI file. This should be a single output fileset I think because the names are always the
        same and we cannnot put everything in a single fileset. Is that useful? Or should we create filesets for
        each organ and add them together?
        """
        if mask_name:
            # Run for single organ/structure
            pass
        else:
            # Run for all organs/structures
            pass
        LOG.info(f'Running Total Segmentator on series {series_instance_uid} with {len(series_files)} scan files...')
        return True
    
    def run(self, task_status_id: str, fileset_id: str, output_fileset_name: str, user :User, mask_name: str) -> bool:
        name = self.name
        LOG.info(f'name: {name}, task_status_id: {task_status_id}, fileset_id: {fileset_id}, output_fileset_name: {output_fileset_name}, mask_name: {mask_name}')
        data_manager = DataManager()
        try:
            if not is_uuid(fileset_id):
                raise TaskException('fileset_id is not UUID')
            fileset = data_manager.get_fileset(fileset_id)
            if fileset is None:
                raise TaskException('fileset is None')
            # Search for CT series within the fileset files
            series_list = self.find_series_in_fileset(fileset, data_manager)
            series_list_keys = list(series_list.keys())
            series_list_values = list(series_list.values())
            nr_steps = len(series_list_keys)
            set_task_status(name, task_status_id, {'status': 'running', 'progress': 0})
            for step in range(len(series_list_keys)):
                series_instance_uid, series_files = series_list_keys[step], series_list_values[step]
                if len(series_files) > 0:
                    if not self.run_totalsegmentator_on_series(series_instance_uid, series_files, mask_name):
                        raise TaskException(f'Could not run Total Segmentator on series {series_instance_uid}')
                else:
                    raise TaskException(f'Empty series {series_instance_uid}')
                progress = int(((step + 1) / (nr_steps)) * 100)
                set_task_status(name, task_status_id, {'status': 'running', 'progress': progress})
            set_task_status(name, task_status_id, {'status': 'completed', 'progress': 100})
            return True
        except TaskException as e:
            LOG.error(f'exception occurred while processing files ({e})')
            set_task_status(name, task_status_id, {'status': 'failed', 'progress': -1})
            return False
        
    @staticmethod
    @login_required
    def view(request: HttpRequest) -> HttpResponse:
        data_manager = DataManager()
        task_manager = TaskManager()
        if request.method == 'POST':
            fileset_id = request.POST.get('fileset_id', None)
            if fileset_id:
                mask_name = request.POST.get('mask_name', None)
                output_fileset_name = request.POST.get('output_fileset_name', None)
                return task_manager.run_task_and_get_response(
                    totalsegmentatortask, fileset_id, output_fileset_name, request.user, mask_name)
            else:
                LOG.warning(f'no segmentation fileset ID selected')
        elif request.method == 'GET':
            response = task_manager.get_response('totalsegmentatortask', request)
            if response:
                return response
        else:
            pass
        filesets = data_manager.get_filesets(request.user)
        task = data_manager.get_task_by_name('totalsegmentatortask')
        return render(request, task.hmtl_page, context={'filesets': filesets, 'task': task})


@task()
def totalsegmentatortask(task_status_id: str, fileset_id: str, output_fileset_name: str, user :User, mask_name: str) -> bool:
    return TotalSegmentatorTask().run(task_status_id, fileset_id, output_fileset_name, user, mask_name)