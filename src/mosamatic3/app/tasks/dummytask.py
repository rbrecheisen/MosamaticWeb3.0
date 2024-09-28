import time

from huey.contrib.djhuey import task

from ..models import TaskModel
from ..utils import create_name_with_timestamp


@task()
def dummy_task():
    for step in range(5):
        print('Running dummy task...')
        time.sleep(1)
    # Return True if task finished successfully, False otherwise
    return 'Finished'