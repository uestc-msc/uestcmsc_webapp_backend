from uestcmsc_webapp_backend.settings import DEBUG, APP_NAME
from .driveitem import OnedriveDriveItem
from .request import onedrive_http_request


class OnedriveDrive:
    uri = ''

    def __init__(self, uri):
        self.uri = uri

    def __str__(self):
        return self.uri

    @property
    def root(self) -> OnedriveDriveItem:
        return OnedriveDriveItem(uri=f"{self.uri}/root")

    @property
    def _approot(self) -> OnedriveDriveItem:
        return OnedriveDriveItem(uri=f"{self.uri}/special/approot")

    def find_file_by_id(self, id: str) -> OnedriveDriveItem:
        return OnedriveDriveItem(uri=f"{self.uri}/items/{id}")

    def find_file_by_path(self, path: str) -> OnedriveDriveItem:
        return self.root.find_file_by_path(path)

    def search(self, keywords: str):
        return onedrive_http_request(self.uri+f"/search(q='{keywords}')")


onedrive_drive = OnedriveDrive(uri='/me/drive')
onedrive_root = onedrive_drive.root

if DEBUG:
    # 开发时的测试文件会放到 名字_dev 文件夹下
    onedrive_approot = onedrive_drive.find_file_by_path(f'/应用/{APP_NAME}_dev')
else:
    onedrive_approot = onedrive_drive._approot
