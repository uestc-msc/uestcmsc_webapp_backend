from django.urls import path
from . import views
from .views import link, file

urlpatterns = [
    path('', views.ActivityListView.as_view(), name='activity_list'),
    path('<int:id>/', views.ActivityDetailView.as_view(), name='activity_detail'),
    path('link/', link.ActivityLinkCreateView.as_view(), name='activity_link_list'),
    path('link/<int:id>/', link.ActivityLinkDetailView.as_view(), name='activity_link_detail'),
    path('<int:id>/file/', file.ActivityFileView.as_view(), name='activity_file_down'),
    path('<int:id>/file/done/', file.ActivityFileDone.as_view(), name='activity_file_done'),
    path('<int:id>/admin/', views.ActivityDetailAdminView.as_view(), name='activity_detail_admin'),
    path('<int:id>/admin/checkin/', views.ActivityAttenderUpdateView.as_view(), name='activity_detail_admin_check_in'),
    path('<int:id>/checkin/', views.ActivityCheckInView.as_view(), name='activity_check_in'),
]