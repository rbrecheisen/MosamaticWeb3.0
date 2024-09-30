import pydicom
import pydicom.errors

from huey.contrib.djhuey import task
from .utils import set_task_progress, delete_task_progress

from ..data.datamanager import DataManager

# If needed, add zero-padding to DICOM image to enlarge image along shortest axis
# Then larger image is scaled down to 512 x 512
# Then DICOM pixel spacing is updated to ensure correct calculation of areas (how to do that?)
# This ChatGPT session explains how to update a DICOM attribute: https://chatgpt.com/c/66fa806e-1a08-800b-81dd-6fd260753341


@task()
def rescaledicomtask(task_progress_id, fileset_id, user):
    """
    Transforms non-square DICOM image to square image by zero-padding along short axis and scaling down to 512 x 512.

    Arguments:
    - task_progress_id: ID of Redis item containing progress
    - fileset_id: ID of fileset to work on
    - user: Current request user
    
    Returns: True or False
    """
    pass