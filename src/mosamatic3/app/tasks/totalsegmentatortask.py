import pydicom
import pydicom.errors

from typing import List, Dict
from huey.contrib.djhuey import task
from django.contrib.auth.models import User
from .taskexception import TaskException
from ..utils import set_task_progress, delete_task_progress, is_uuid
from ..data.datamanager import DataManager
from ..data.logmanager import LogManager
from ..models import FileModel, FileSetModel

LOG = LogManager()


def find_series_in_fileset(fileset: FileSetModel, data_manager: DataManager) -> Dict[str, FileModel]:
    scans = {}
    files = data_manager.get_files(fileset)
    for f in files:
        p = pydicom.dcmread(f.path, stop_before_pixels=True)
        if p.SeriesInstanceUID not in scans.keys():
            scans[p.SeriesInstanceUID] = []
        scans[p.SeriesInstanceUID].append(f)
    return scans


def run_totalsegmentator_on_series(series_instance_uid: str, series_files: List[FileModel]) -> bool:
    LOG.info(f'Running Total Segmentator on series {series_instance_uid} with {len(series_files)} scan files...')
    return True


@task()
def totalsegmentatortask(task_progress_id: str, fileset_id: str, output_fileset_name: str, user :User) -> bool:
    name = 'totalsegmentatortask'
    LOG.info(f'name: {name}, task_progress_id: {task_progress_id}, fileset_id: {fileset_id}, output_fileset_name: {output_fileset_name}')
    data_manager = DataManager()
    try:
        if not is_uuid(fileset_id):
            raise TaskException('totalsegmentatortask() fileset_id is not UUID')
        fileset = data_manager.get_fileset(fileset_id)
        if fileset is None:
            raise TaskException('totalsegmentatortask() fileset is None')
        files = data_manager.get_files(fileset)

        # Search for CT series within the fileset files
        series = find_series_in_fileset(fileset, data_manager)
        series_keys = list(series.keys())
        series_values = list(series.values())
        nr_steps = len(series_keys)
        set_task_progress(name, task_progress_id, 0)
        for step in range(len(series_keys)):
            series_instance_uid, series_files = series_keys[step], series_values[step]
            if len(series_files) > 0:
                if not run_totalsegmentator_on_series(series_instance_uid, series_files):
                    raise TaskException(f'Could not run Total Segmentator on series {series_instance_uid}')
            else:
                raise TaskException(f'Empty series {series_instance_uid}')
            progress = int(((step + 1) / (nr_steps)) * 100)
            set_task_progress(name, task_progress_id, progress)

        # output_fileset = data_manager.create_fileset(user, output_fileset_name)
        # create separate FileModel objects
        delete_task_progress(name, task_progress_id)
        return True
    except TaskException as e:
        LOG.error(f'totalsegmentatortask() exception occurred while processing files ({e})')
        return False