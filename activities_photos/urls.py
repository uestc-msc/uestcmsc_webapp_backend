from django.urls import path
from . import views

urlpatterns = [
    path('', views.ActivityPhotoListView.as_view(), name='activity_photo_list'),
    path('<int:id>/', views.ActivityPhotoDetailView.as_view(), name='activity_photo_detail'),
]