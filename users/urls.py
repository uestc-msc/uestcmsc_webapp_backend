from django.urls import path
from . import views

urlpatterns = [
    path('', views.UserView.as_view(), name='userlist'),
    # path('<int:pk>/', views.userprof.as_view(), name='userprofile')
]