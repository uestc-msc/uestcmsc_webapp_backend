from uestcmsc_webapp_backend.settings import DEBUG, APP_NAME
from .driveitem import DriveItem
from .utils import onedrive_http_request


class Drive:
    uri = ''

    def __init__(self, uri):
        self.uri = uri

    def __str__(self):
        return self.uri

    @property
    def root(self) -> DriveItem:
        return DriveItem(uri=f"{self.uri}/root")

    @property
    def approot(self) -> DriveItem:
        return DriveItem(uri=f"{self.uri}/special/approot")

    def find_file_by_id(self, id: str) -> DriveItem:
        return DriveItem(uri=f"{self.uri}/items/{id}")

    def find_file_by_path(self, path: str) -> DriveItem:
        return self.root.find_file_by_path(path)

    def search(self, keywords: str):
        return onedrive_http_request(self.uri+f"/search(q='{keywords}')")


drive = Drive(uri='/me/drive')
drive_root = drive.root

if not DEBUG:
    app_root = drive.approot
else:
    app_root = drive.find_file_by_path(f'/应用/{APP_NAME}_dev')
