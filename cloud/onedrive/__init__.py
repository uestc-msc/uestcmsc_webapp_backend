from rest_framework import status

from uestcmsc_webapp_backend.settings import APP_NAME, DEBUG
from .auth import OnedriveAuthentication, OnedriveUnavailableException
from .api import Drive, DriveItem, drive, drive_root, app_root
from utils.asynchronous import asynchronous

refresh_access_token = OnedriveAuthentication.refresh_access_token
activity_directory = app_root.find_file_by_path('沙龙')
temp_directory = app_root.find_file_by_path('temp')


@asynchronous
def initialize_onedrive():
    if DEBUG:
        drive_root.create_directory_recursive(f'/应用/{APP_NAME}_dev')
    for dirname in ['沙龙', 'temp']:
        response = app_root.create_directory(dirname, 'fail', fail_silently=False)
        if not response.ok and not response.status_code == status.HTTP_409_CONFLICT:
            raise OnedriveUnavailableException(detail=f"初始化文件夹失败：{dirname}")
