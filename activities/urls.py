from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.ActivityListView.as_view(), name='activity_list'),
    path('<int:id>/', views.ActivityDetailView.as_view(), name='activity_detail'),
    path('<int:id>/admin/', views.ActivityDetailAdminView.as_view(), name='activity_detail_admin'),
    path('<int:id>/admin/checkin/', views.ActivityAttenderUpdateView.as_view(), name='activity_detail_admin_check_in'),
    path('<int:id>/checkin/', views.ActivityCheckInView.as_view(), name='activity_check_in'),
    path('link/', include('activities_links.urls')),
    path('file/', include('activities_files.urls')),
    path('photo/', include('activities_photos.urls')),
]