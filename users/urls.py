from django.urls import path
from . import views

urlpatterns = [
    path('', views.UserListView.as_view(), name='userlist'),
    path('<int:pk>/', views.UserProfileView.as_view(), name='userprofile')
]