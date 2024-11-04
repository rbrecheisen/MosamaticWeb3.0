from django.urls import path

from .views.base import auth, custom_logout
from .views.filesets import fileset, filesets
from .views.tasks import tasks, task
from .views.logs import logs
from .tasks.taskloader import TaskLoader
from .data.logmanager import LogManager

LOG = LogManager()


urlpatterns = [
    path('', filesets),
    path('auth', auth),
    path('filesets/', filesets),
    path('filesets/<str:fileset_id>', fileset),
    path('accounts/logout/', custom_logout, name='logout'),
    path('logs/', logs),
    path('tasks/', tasks),
    path('tasks/<str:task_name>', task),
]

tasks = TaskLoader().run()
for task in tasks:
    urlpatterns.append(path(task.url_pattern[1:], task.view))
    LOG.info(f'Added URL pattern for task {task.name}: ({task.url_pattern[1:]})')