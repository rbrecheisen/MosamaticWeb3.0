from django.urls import path

from .views.base import auth, custom_logout
from .views.filesets import fileset, filesets
from .views.tasks.tasks import tasks
from .views.tasks.dummy import dummy
from .views.tasks.dummyparams import dummyparams
from .views.tasks.filterdicom import filterdicom


urlpatterns = [
    path('', filesets),
    path('auth', auth),
    path('filesets/', filesets),
    path('filesets/<str:fileset_id>', fileset),
    path('accounts/logout/', custom_logout, name='logout'),

    # Tasks
    path('tasks/', tasks),
    path('tasks/dummy/', dummy),
    path('tasks/dummyparams/', dummyparams),
    path('tasks/filterdicom/', filterdicom),
]
