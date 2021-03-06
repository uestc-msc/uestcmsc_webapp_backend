from __future__ import annotations

import requests

from .utils import validate_path, onedrive_http_request
from .. import OnedriveUnavailableException


class DriveItem:
    def __init__(self, uri: str = None):
        self.uri = uri

    def __str__(self):
        return self.uri

    def find_file_by_path(self, path: str) -> DriveItem:
        path = validate_path(path)
        if path == '/':
            return DriveItem(uri=self.uri)
        uri = f"{self.uri}:{path}:"  # 如果 self.uri 自带 ':' 和后面形成了 '::'，应该去掉
        uri = uri.replace('::', '')
        return DriveItem(uri=uri)

    def find_file_by_id(self, id: str) -> DriveItem:
        return DriveItem(uri=f"{self.uri}/items/{id}")

    def search(self, keywords: str, fail_silently=False) -> requests.Response:
        return onedrive_http_request(self.uri + f"/search(q='{keywords}')", fail_silently=fail_silently)

    def get_metadata(self, fail_silently=False) -> requests.Response:
        return onedrive_http_request(self.uri, fail_silently=fail_silently)

    def get_thumbnail(self, thumb_id=0, size='large', fail_silently=False) -> requests.Response:
        return onedrive_http_request(self.uri + f'/thumbnails/{thumb_id}/{size}', fail_silently=fail_silently)

    def list_children(self, fail_silently=False) -> requests.Response:
        return onedrive_http_request(self.uri + '/children', fail_silently=fail_silently)

    def create_directory(self,
                         dirname: str,
                         conflict_behavior: str = 'fail',
                         fail_silently=False) -> requests.Response:
        assert conflict_behavior in ('fail', 'replace' 'rename')
        return onedrive_http_request(self.uri + '/children', 'POST', {
            "name": dirname,
            "folder": {},
            "@microsoft.graph.conflictBehavior": conflict_behavior
        }, fail_silently=fail_silently)

    def create_directory_recursive(self, path: str) -> requests.Response:
        # 由于多数时候都只需要创建子文件夹
        # 因此从尝试创建子文件夹开始，从下往上尝试创建
        # 在某层成功后又逐步往下
        path_list = path.strip('/').split('/')
        depth = len(path_list)
        response = requests.Response()
        response.status_code = 500

        while not response.ok:
            depth -= 1
            if depth < 0:
                break
            cur_path = '/'.join(path_list[0:depth])
            new_dir = path_list[depth]
            response = self.find_file_by_path(cur_path).create_directory(new_dir, 'fail', fail_silently=True)

        while depth < len(path_list) - 1:
            depth += 1
            cur_path = '/'.join(path_list[0:depth])
            new_dir = path_list[depth]
            response = self.find_file_by_path(cur_path).create_directory(new_dir, 'fail', fail_silently=True)
        return response

    # https://docs.microsoft.com/zh-cn/onedrive/developer/rest-api/api/driveitem_copy?view=odsp-graph-online
    def copy(self,
             destination: dict,
             new_filename: str = None,
             fail_silently=False) -> requests.Response:
        json = {"parentReference": destination}
        if new_filename:
            json['name'] = new_filename
        return onedrive_http_request(self.uri + '/copy', 'POST', json, fail_silently=fail_silently)

    def move(self,
             destination: dict,
             new_filename: str = None,
             fail_silently=False) -> requests.Response:
        json = {"parentReference": destination}
        if new_filename:
            json['name'] = new_filename
        return onedrive_http_request(self.uri, 'PATCH', json, fail_silently=fail_silently)

    def delete(self, fail_silently=False) -> requests.Response:
        return onedrive_http_request(self.uri, 'DELETE', fail_silently=fail_silently)

    def download(self, fail_silently=False) -> requests.Response:
        return onedrive_http_request(self.uri + '/content', fail_silently=fail_silently)

    # filename 为空时，执行上传操作，文件内容放在 data 中，Onedrive 创建或更新 DriveItem（文件）
    # filename 不为空时，在 DriveItem（目录）上传该文件
    def upload(self, data, conflict_behavior: str = 'fail', fail_silently=False) -> requests.Response:
        return onedrive_http_request(self.uri + f'/content?@microsoft.graph.conflictBehavior={conflict_behavior}',
                                     'PUT', data=data, fail_silently=fail_silently)

    # 仅 Onedrive 个人可使用
    def upload_via_url(self,
                       source_url: str,
                       filename: str = None,
                       conflict_behavior: str = 'fail',
                       fail_silently=False) -> requests.Response:
        assert conflict_behavior in ('fail', 'replace' 'rename')
        json = {
            "@microsoft.graph.sourceUrl": source_url,
            "@microsoft.graph.conflictBehavior": conflict_behavior,
            "file": {}
        }
        if filename:
            json['name'] = 'filename'
        return onedrive_http_request(self.uri + '/children', 'POST', json, extra_headers={"Prefer": "respond-async"},
                                     fail_silently=fail_silently)

    # 上传大文件，创建会话后，需向返回的 uploadUrl 进行 PUT
    # https://docs.microsoft.com/zh-cn/onedrive/developer/rest-api/api/driveitem_createuploadsession?view=odsp-graph-online
    def create_upload_session(self,
                              conflict_behavior: str = 'fail',
                              fail_silently=False) -> requests.Response:
        assert conflict_behavior in ('fail', 'replace' 'rename')
        return onedrive_http_request(self.uri + '/createUploadSession', 'POST', {
            "item": {"@microsoft.graph.conflictBehavior": conflict_behavior}
        }, fail_silently=fail_silently)

    def create_link(self, fail_silently=False) -> requests.Response:
        return onedrive_http_request(self.uri + '/createLink', 'POST', {
            "type": "view",
            "scope": "anonymous"
        }, fail_silently=fail_silently)

    # 注意这个链接还是有 redirect 的过程，所以
    def get_download_link(self, fail_silently=False) -> str:
        response = self.create_link(fail_silently=fail_silently)
        share_link = response.json()['link']['webUrl']
        download_link = share_link.split('?')[0] + '?download=1'
        return download_link
