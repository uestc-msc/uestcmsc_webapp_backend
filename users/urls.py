from django.urls import path
from . import views

urlpatterns = [
    path('', views.UserListView.as_view(), name='user_list'),
    path('<int:id>/', views.UserDetailView.as_view(), name='user_detail'),
    path('whoami/', views.whoami_view, name='users_whoami')
]