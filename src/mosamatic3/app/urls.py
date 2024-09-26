from django.urls import path

from .views.base import auth, custom_logout
from .views.filesets import fileset, filesets
from .views.dicomstructure import dicomstructure
from .views.tasks.tasks import tasks
from .views.tasks.mfal3ct import mfal3ct
from .views.tasks.mfadixon import mfadixon


urlpatterns = [
    path('', filesets),
    path('auth', auth),
    path('filesets/', filesets),
    path('filesets/<str:fileset_id>', fileset),
    path('filesets/<str:fileset_id>/dicomstructure/', dicomstructure),
    path('accounts/logout/', custom_logout, name='logout'),
    path('tasks/', tasks),
    path('tasks/mfal3ct/', mfal3ct),
    path('tasks/mfadixon/', mfadixon),
]
