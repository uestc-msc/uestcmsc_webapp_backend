from rest_framework import status

from uestcmsc_webapp_backend.settings import APP_NAME, DEBUG
from .auth import OnedriveAuthentication, OnedriveUnavailableException
from .api import OnedriveDrive, OnedriveDriveItem, onedrive_drive, onedrive_root, onedrive_approot
from utils.asynchronous import asynchronous

onedrive_activity_directory = onedrive_approot.find_file_by_path('沙龙')
onedrive_temp_directory = onedrive_approot.find_file_by_path('temp')


@asynchronous
def initialize_onedrive():
    # 初始化文件夹
    if DEBUG:
        onedrive_root.create_directory_recursive(f'/应用/{APP_NAME}_dev')
    for dirname in ['沙龙', 'temp']:
        response = onedrive_approot.create_directory(dirname, 'fail', fail_silently=False)
        if not (response.ok or response.status_code == status.HTTP_409_CONFLICT):
            raise OnedriveUnavailableException(detail=f"初始化文件夹失败：{dirname}")
