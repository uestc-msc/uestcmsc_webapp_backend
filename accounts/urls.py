from django.urls import path
from . import views

urlpatterns = [
    path('change_password/', views.change_password, name='change_password'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('forget_password/', views.forget_password, name='forget_password'),
    path('reset_password/', views.reset_password, name='reset_password')
]