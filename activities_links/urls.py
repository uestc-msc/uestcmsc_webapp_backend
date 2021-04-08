from django.urls import path
from . import views

urlpatterns = [
    path('', views.ActivityLinkListView.as_view(), name='activity_link_list'),
    path('<int:id>/', views.ActivityLinkDetailView.as_view(), name='activity_link_detail'),
]