from django.urls import path

from cloud.views.api import onedrive_create_upload_session, onedrive_upload_done
from cloud.views.login import onedrive_login, onedrive_login_callback
from cloud.views.status import onedrive_status

urlpatterns = [
    path('login/', onedrive_login, name='onedrive_login'),
    path('login_callback/', onedrive_login_callback, name='onedrive_login_callback'),
    path('status/', onedrive_status, name='onedrive_status'),

    path('upload/', onedrive_create_upload_session, name='onedrive_create_upload_session'),
    path('upload/done/', onedrive_upload_done, name='onedrive_upload_done')
]
