import time

from huey.contrib.djhuey import task

# from ..models import TaskProgressModel


@task()
def dummy_task():
    nr_steps = 5
    for step in range(nr_steps):
        print(f'Running dummy task ({step})...')
        time.sleep(1)
    return True


# @task()
# def dummy_task(task_progress_id):
#     try:
#         task_progress = TaskProgressModel.objects.get(pk=task_progress_id)
#         nr_steps = 5
#         for step in range(nr_steps):
#             print('Running dummy task...')
#             time.sleep(1)
#             task_progress.progress = int(((step + 1) / (nr_steps)) * 100)
#             task_progress.status = 'running'
#             task_progress.save()
#         task_progress.progress = 100
#         task_progress.status = 'completed'
#         task_progress.save()
#     except TaskProgressModel.DoesNotExist:
#         print(f'TaskProgressModel does not exist')
#         return False
#     return True