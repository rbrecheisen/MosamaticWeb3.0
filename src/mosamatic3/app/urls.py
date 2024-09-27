from django.urls import path

from .views.base import auth, custom_logout
from .views.filesets import fileset, filesets
from .views.tasks.tasks import tasks
from .views.tasks.dummy import dummy
from .views.tasks.filterdicom import filterdicom
from .views.tasks.transformdicom import transformdicom
from .views.tasks.musclefatsegmentation import musclefatsegmentation
from .views.tasks.calculatebodycompositionmetrics import calculatebodycompositionmetrics


urlpatterns = [
    path('', filesets),
    path('auth', auth),
    path('filesets/', filesets),
    path('filesets/<str:fileset_id>', fileset),
    path('accounts/logout/', custom_logout, name='logout'),
    path('tasks/', tasks),
    path('tasks/dummy/', dummy),
    path('tasks/filterdicom/', filterdicom),
    path('tasks/transformdicom/', transformdicom),
    path('tasks/musclefatsegmentation/', musclefatsegmentation),
    path('tasks/calculatebodycompositionmetrics/', calculatebodycompositionmetrics),
]
