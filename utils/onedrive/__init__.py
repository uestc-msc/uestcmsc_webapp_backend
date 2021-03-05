from .auth import OnedriveAuthentication, OnedriveUnavailableException
from .api import Drive, DriveItem, drive, drive_root, app_root

refresh_access_token = OnedriveAuthentication.refresh_access_token
activity_directory = app_root.find_file_by_path('沙龙')
temp_directory = app_root.find_file_by_path('temp')
