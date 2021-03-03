from __future__ import annotations

import requests

from .utils import validate_path, onedrive_http_request


class DriveItem:
    def __init__(self, uri: str = None):
        self.uri = uri

    def __str__(self):
        return self.uri

    def find_file_by_path(self, path: str) -> DriveItem:
        path = validate_path(path)
        uri = f"{self.uri}:{path}:"  # 如果 self.uri 自带 ':' 和后面形成了 '::'，应该去掉
        uri = uri.replace('::', '')
        return DriveItem(uri=uri)

    def find_file_by_id(self, id: str) -> DriveItem:
        return DriveItem(uri=f"{self.uri}/items/{id}")

    def search(self, keywords: str) -> requests.Response:
        return onedrive_http_request(self.uri + f"/search(q='{keywords}')")

    def get_metadata(self) -> requests.Response:
        return onedrive_http_request(self.uri)

    def get_thumbnail(self, thumb_id=0, size='large'):
        return onedrive_http_request(self.uri + f'/thumbnails/{thumb_id}/{size}')

    def list_children(self) -> requests.Response:
        return onedrive_http_request(self.uri + '/children')

    def create_directory(self, dirname: str, conflict_behavior: str = 'fail') -> requests.Response:
        assert conflict_behavior in ('fail', 'replace' 'rename')
        return onedrive_http_request(self.uri + '/children', 'POST', {
            "name": dirname,
            "folder": {},
            "@microsoft.graph.conflictBehavior": conflict_behavior
        })

    # https://docs.microsoft.com/zh-cn/onedrive/developer/rest-api/api/driveitem_copy?view=odsp-graph-online
    def copy(self, destination: dict, new_filename: str = None):
        json = {"parentReference": destination}
        if new_filename:
            json['name'] = new_filename
        return onedrive_http_request(self.uri + '/copy', 'POST', json)

    def move(self, destination: dict, new_filename: str = None):
        json = {"parentReference": destination}
        if new_filename:
            json['name'] = new_filename
        return onedrive_http_request(self.uri, 'PATCH', json)

    def delete(self):
        return onedrive_http_request(self.uri, 'DELETE')

    def download(self) -> requests.Response:
        return onedrive_http_request(self.uri + '/content')

    # filename 为空时，执行上传操作，文件内容放在 data 中，Onedrive 创建或更新 DriveItem（文件）
    # filename 不为空时，在 DriveItem（目录）上传该文件
    def upload(self, data, conflict_behavior: str = 'fail') -> requests.Response:
        return onedrive_http_request(self.uri + f'/content?@microsoft.graph.conflictBehavior={conflict_behavior}',
                                     'PUT', data=data)

    def upload_via_url(self, source_url: str, filename: str = None,
                       conflict_behavior: str = 'fail') -> requests.Response:
        assert conflict_behavior in ('fail', 'replace' 'rename')
        json = {
            "@microsoft.graph.sourceUrl": source_url,
            "@microsoft.graph.conflictBehavior": conflict_behavior,
            "file": {}
        }
        if filename:
            json['name'] = 'filename'
        return onedrive_http_request(self.uri + '/children', 'POST', json,
                                     extra_headers={"Prefer": "respond-async"})

    # ????
    # 上传大文件，创建会话后，需向返回的 uploadUrl 进行 PUT
    # https://docs.microsoft.com/zh-cn/onedrive/developer/rest-api/api/driveitem_createuploadsession?view=odsp-graph-online
    def create_upload_session(self, conflict_behavior: str = 'fail') -> requests.Response:
        assert conflict_behavior in ('fail', 'replace' 'rename')
        return onedrive_http_request(self.uri + '/createUploadSession', 'POST', {
            "item": {
                "@microsoft.graph.conflictBehavior": conflict_behavior,
            }
        })

    def create_link(self) -> requests.Response:
        return onedrive_http_request(self.uri + '/createLink', 'POST', {
            "type": "view",
            "scope": "anonymous"
        })

    # 注意这个链接还是有 redirect 的过程，所以
    def get_download_link(self) -> str:
        response = self.create_link()
        share_link = response.json()['link']['webUrl']
        download_link = share_link.split('?')[0] + '?download=1'
        return download_link


app_root = DriveItem(uri='/me/drive/special/approot')