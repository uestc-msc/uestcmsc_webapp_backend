from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.onedrive_login, name='onedrive_login'),
    path('login_callback/', views.onedrive_login_callback, name='onedrive_login_callback'),
    path('status/', views.onedrive_status, name='onedrive_status')
]
