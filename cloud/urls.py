from django.urls import path

from cloud.views.login import onedrive_login_view, onedrive_login_callback_view
from cloud.views.status import onedrive_status_view
from cloud.views.file import OnedriveFileView, OnedriveFileDownloadView

urlpatterns = [
    path('login/', onedrive_login_view, name='onedrive_login'),
    path('login_callback/', onedrive_login_callback_view, name='onedrive_login_callback'),
    path('status/', onedrive_status_view, name='onedrive_status'),
    path('file/', OnedriveFileView.as_view(), name='onedrive_file'),
    path('file/<str:id>/download/', OnedriveFileDownloadView.as_view(), name='onedrive_file_download')
]
