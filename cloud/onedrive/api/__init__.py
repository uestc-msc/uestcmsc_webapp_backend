from .drive import OnedriveDrive, onedrive_drive, onedrive_root, onedrive_approot
from .driveitem import OnedriveDriveItem

# https://docs.microsoft.com/zh-cn/graph/concepts/addressing-driveitems#onedrive-reserved-characters
onedrive_business_reserved = r"/\*<>?:|#%"
onedrive_business_reserved_re = r"[/\\*<>?:|#%]"    # 正则表达式
