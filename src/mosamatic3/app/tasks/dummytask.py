import time

from celery import shared_task


@shared_task
def dummy_task():
    for i in range(5):
        print('Running dummy task...')
        time.sleep()
    print('Finished')