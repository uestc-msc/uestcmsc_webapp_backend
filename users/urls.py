from django.urls import path
from . import views

urlpatterns = [
    path('', views.UserView.as_view(), name='userlist'),
    # path('<int:pk>/', views.userprof.as_view(), name='userprofile'),
    path('<int:pk>/password/', views.reset_password_by_password, name='reset_password_by_password'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('forgetpassword/', views.forget_password, name='forget_password'),
    path('resetpassword/', views.reset_password_by_token, name='reset_password_by_token')
]