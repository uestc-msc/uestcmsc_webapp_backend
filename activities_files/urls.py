from django.urls import path
from . import views

urlpatterns = [
    path('', views.ActivityFileListView.as_view(), name='activity_file_list'),
    path('<str:id>/', views.ActivityFileDetailView.as_view(), name='activity_file_detail'),
]