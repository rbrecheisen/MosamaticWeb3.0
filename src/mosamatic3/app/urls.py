from django.urls import path
from . import views


urlpatterns = [
    path('', views.filesets),
    path('auth', views.auth),
    path('filesets/', views.filesets),
    path('filesets/<str:fileset_id>', views.fileset),
    path('filesets/<str:fileset_id>/dicomstructure', views.dicomstructure),
    path('accounts/logout/', views.custom_logout, name='logout'),
]
