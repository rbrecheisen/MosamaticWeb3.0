from __future__ import absolute_import, unicode_literals

import os

from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mosamatic3.settings')

app = Celery('mosamatic3')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()