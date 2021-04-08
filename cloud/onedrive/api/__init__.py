from .drive import OnedriveDrive, onedrive_drive, onedrive_root, onedrive_approot
from .driveitem import OnedriveDriveItem

# https://docs.microsoft.com/zh-cn/onedrive/developer/rest-api/concepts/addressing-driveitems?view=odsp-graph-online#onedrive-reserved-characters
onedrive_business_reserved = r"/\*<>?:|#%"
