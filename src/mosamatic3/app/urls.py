from django.urls import path

from .views.base import auth, custom_logout
from .views.filesets import fileset, filesets
from .views.tasks.tasks import tasks
from .views.tasks.dummy import dummy
from .views.healthcheck import HealthCheck


urlpatterns = [
    path('', filesets),
    path('auth', auth),
    path('filesets/', filesets),
    path('filesets/<str:fileset_id>', fileset),
    path('accounts/logout/', custom_logout, name='logout'),
    path('tasks/', tasks),
    path('tasks/dummy/', dummy),
    path('health/', HealthCheck.as_view()),
]
