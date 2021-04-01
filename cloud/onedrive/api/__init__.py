from .drive import Drive, drive, drive_root, app_root
from .driveitem import DriveItem

# https://docs.microsoft.com/zh-cn/onedrive/developer/rest-api/concepts/addressing-driveitems?view=odsp-graph-online#onedrive-reserved-characters
onedrive_business_reserved = r"/\*<>?:|#%"
