import time

from huey.contrib.djhuey import task


@task()
def dummy_task():
    for i in range(5):
        print('Running dummy task...')
        time.sleep(1)
    print('Finished')