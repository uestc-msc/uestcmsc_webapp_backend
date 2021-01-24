from django.urls import path
from . import views

urlpatterns = [
    path('', views.ActivityListView.as_view(), name='activity_list'),
    path('<int:id>/', views.ActivityDetailView.as_view(), name='activity_detail'),
    path('<int:id>/admin/', views.ActivityDetailAdminView.as_view(), name='activity_detail_admin'),
    path('<int:id>/check_in_admin/', views.ActivityAttenderUpdateView.as_view(), name='activity_check_in_admin'),
    path('<int:id>/check_in/', views.ActivityCheckInView.as_view(), name='activity_check_in')
]