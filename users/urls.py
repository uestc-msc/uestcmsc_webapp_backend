from django.urls import path
from . import views

urlpatterns = [
    path('', views.UserView.as_view(), name='user'),
    # path('<int:pk>/', views, name='profile'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('forget_password/', views.forget_password, name='forget_password'),
    path('reset_password/', views.reset_password, name='reset_password'),
]