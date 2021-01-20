from django.urls import path
from . import views

urlpatterns = [
    path('', views.ActivityListView.as_view(), name='activity_list'),
    path('<int:pk>/', views.ActivityDetailView.as_view(), name='activity_detail'),
    path('check_in/', views.activity_check_in, name='activity_check_in')
]