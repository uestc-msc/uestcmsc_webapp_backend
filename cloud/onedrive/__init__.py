import logging

import requests
from rest_framework import status

from uestcmsc_webapp_backend.settings import APP_NAME, DEBUG
from cloud.onedrive.api.auth import OnedriveAuthentication, OnedriveUnavailableException
from utils.asynchronous import run_in_new_thread
from .api import OnedriveDrive, OnedriveDriveItem, onedrive_drive, onedrive_root, onedrive_approot

onedrive_activity_directory = onedrive_approot.find_file_by_path('沙龙')
onedrive_temp_directory = onedrive_approot.find_file_by_path('temp')

logger = logging.getLogger(__name__)


@run_in_new_thread
def initialize_onedrive():
    # 初始化文件夹
    if DEBUG:
        onedrive_root.create_directory_recursive(f'/应用/{APP_NAME}_dev')
    for dirname in ['沙龙', 'temp']:
        response = onedrive_approot.create_directory(dirname, 'fail', fail_silently=True)
        if response.is_error and not response.status_code == status.HTTP_409_CONFLICT:
            logger.error(f"Onedrive 初始化文件夹失败：{dirname}", stack_info=True)
            raise OnedriveUnavailableException
