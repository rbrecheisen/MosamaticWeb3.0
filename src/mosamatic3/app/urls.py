from django.urls import path
from . import views


urlpatterns = [
    path('', views.filesets),
    path('auth', views.auth),
    path('progress', views.progress),
    path('filesets/', views.filesets),
    path('filesets/<str:fileset_id>', views.fileset),
]
