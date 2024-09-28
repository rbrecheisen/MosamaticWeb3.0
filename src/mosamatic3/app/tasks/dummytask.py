import time

from huey.contrib.djhuey import task

from ..models import TaskModel
from ..utils import create_name_with_timestamp


@task(include_task=True)
def dummy_task(task):
    task_id = task.task_id
    # Calculate nr. steps
    task = TaskModel.objects.create(
        name=create_name_with_timestamp('dummy_task'),
        task_id=task_id,
        nr_steps=10,
        status='running',
    )
    for step in range(10):
        print('Running dummy task...')
        time.sleep(1)
        task.progress = int(((step + 1) / (task.nr_steps)) * 100)
        task.save()
    print('Finished')