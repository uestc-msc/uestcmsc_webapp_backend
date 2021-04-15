from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('forgetpassword/', views.forget_password, name='forget_password'),
    path('resetpassword/', views.reset_password, name='reset_password'),
]