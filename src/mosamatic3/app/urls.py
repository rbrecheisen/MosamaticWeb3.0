from django.urls import path
from . import views


urlpatterns = [
    path('', views.datasets),
    path('auth', views.auth),
    # path('progress', views.progress),
    path('datasets/', views.datasets),
    path('datasets/<str:dataset_id>', views.dataset),
]
