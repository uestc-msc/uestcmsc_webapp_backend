from django.urls import path

from cloud.views.login import onedrive_login, onedrive_login_callback
from cloud.views.status import onedrive_status
from cloud.views.file import OnedriveFileView, onedrive_file_upload_done

urlpatterns = [
    path('login/', onedrive_login, name='onedrive_login'),
    path('login_callback/', onedrive_login_callback, name='onedrive_login_callback'),
    path('status/', onedrive_status, name='onedrive_status'),
    path('file/', OnedriveFileView.as_view(), name='onedrive_file'),
    path('file/upload_done/', onedrive_file_upload_done, name='onedirve_file_upload_done')
]
