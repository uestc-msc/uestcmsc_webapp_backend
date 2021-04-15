from __future__ import annotations

import requests

from .request import validate_path, onedrive_http_request


class OnedriveDriveItem:
    def __init__(self, uri: str = None):
        self.uri = uri

    def __str__(self):
        return self.uri

    # 根据路径找到文件（夹）
    def find_file_by_path(self, path: str) -> OnedriveDriveItem:
        path = validate_path(path)
        if path == '/':
            return OnedriveDriveItem(uri=self.uri)
        uri = f"{self.uri}:{path}:"  # 如果 self.uri 自带 ':' 和后面形成了 '::'，应该去掉
        uri = uri.replace('::', '')
        return OnedriveDriveItem(uri=uri)

    # 根据 DriveItem id 找到文件（夹）
    def find_file_by_id(self, id: str) -> OnedriveDriveItem:
        return OnedriveDriveItem(uri=f"{self.uri}/items/{id}")

    # 在当前目录下进行搜索
    # https://docs.microsoft.com/zh-cn/onedrive/developer/rest-api/api/driveitem_search?view=odsp-graph-online
    def search(self, keywords: str, fail_silently=False) -> requests.Response:
        return onedrive_http_request(self.uri + f"/search(q='{keywords}')", fail_silently=fail_silently)

    # 获取文件元信息
    # https://docs.microsoft.com/zh-cn/onedrive/developer/rest-api/api/driveitem_get?view=odsp-graph-online
    def get_metadata(self, fail_silently=False) -> requests.Response:
        return onedrive_http_request(self.uri, fail_silently=fail_silently)

    # 获取大缩略图
    # https://docs.microsoft.com/zh-cn/onedrive/developer/rest-api/api/driveitem_list_thumbnails#get-a-single-thumbnail
    def get_single_thumbnail(self, thumb_id=0, size='large', fail_silently=False) -> str:
        response = onedrive_http_request(self.uri + f'/thumbnails/{thumb_id}/{size}', fail_silently=fail_silently)
        return response.json()['url']

    # 列出文件夹下内容
    # https://docs.microsoft.com/zh-cn/onedrive/developer/rest-api/api/driveitem_list_children?view=odsp-graph-online
    def list_children(self, fail_silently=False) -> requests.Response:
        return onedrive_http_request(self.uri + '/children', fail_silently=fail_silently)

    # 创建文件夹
    # https://docs.microsoft.com/zh-cn/onedrive/developer/rest-api/api/driveitem_post_children?view=odsp-graph-online
    def create_directory(self,
                         dirname: str,
                         conflict_behavior: str = 'fail',
                         fail_silently=False) -> requests.Response:
        assert conflict_behavior in ('fail', 'replace', 'rename')
        return onedrive_http_request(self.uri + '/children', 'POST', {
            "name": dirname,
            "folder": {},
            "@microsoft.graph.conflictBehavior": conflict_behavior
        }, fail_silently=fail_silently)

    # 递归地创建多级文件夹
    # 成功后返回最底层文件夹的信息，见：
    # https://docs.microsoft.com/zh-cn/onedrive/developer/rest-api/api/driveitem_post_children?view=odsp-graph-online
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

    # 复制文件，可指定新文件名
    # 如果发生文件冲突，会 fail
    # https://docs.microsoft.com/zh-cn/onedrive/developer/rest-api/api/driveitem_copy?view=odsp-graph-online
    def copy(self,
             dest_dir_id: str,
             new_filename: str = None,
             fail_silently=False) -> requests.Response:
        json = {"parentReference": {"id": dest_dir_id}}
        if new_filename:
            json['name'] = new_filename
        return onedrive_http_request(self.uri + '/copy', 'POST', json, fail_silently=fail_silently)

    # 移动文件，可指定新文件名
    # 如果发生文件冲突，会 fail
    # https://docs.microsoft.com/zh-cn/onedrive/developer/rest-api/api/driveitem_move?view=odsp-graph-online
    def move(self,
             dest_dir_id: str,
             new_filename: str = None,
             fail_silently=False) -> requests.Response:
        json = {"parentReference": {"id": dest_dir_id}}
        if new_filename:
            json['name'] = new_filename
        return onedrive_http_request(self.uri, 'PATCH', json, fail_silently=fail_silently)

    # 删除文件
    # https://docs.microsoft.com/zh-cn/onedrive/developer/rest-api/api/driveitem_delete?view=odsp-graph-online
    def delete(self, fail_silently=False) -> requests.Response:
        return onedrive_http_request(self.uri, 'DELETE', fail_silently=fail_silently)

    # 下载文件
    # https://docs.microsoft.com/zh-cn/onedrive/developer/rest-api/api/driveitem_get_content?view=odsp-graph-online
    def download(self, fail_silently=False) -> requests.Response:
        return onedrive_http_request(self.uri + '/content', fail_silently=fail_silently)

    # 上传文件，文件内容放在 data 中
    # DriveItem 应当为文件的路径，Onedrive 会创建或更新该文件
    # https://docs.microsoft.com/zh-cn/onedrive/developer/rest-api/api/driveitem_put_content?view=odsp-graph-online
    def upload(self, data, conflict_behavior: str = 'fail', fail_silently=False) -> requests.Response:
        return onedrive_http_request(self.uri + f'/content?@microsoft.graph.conflictBehavior={conflict_behavior}',
                                     'PUT', data=data, fail_silently=fail_silently)

    # 通过 URL 上传文件，类似于离线下载，仅 Onedrive 个人可使用该 API
    # https://docs.microsoft.com/zh-cn/onedrive/developer/rest-api/api/driveitem_upload_url?view=odsp-graph-online
    def upload_via_url(self,
                       source_url: str,
                       filename: str = None,
                       conflict_behavior: str = 'fail',
                       fail_silently=False) -> requests.Response:
        assert conflict_behavior in ('fail', 'replace', 'rename')
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
        assert conflict_behavior in ('fail', 'replace', 'rename')
        return onedrive_http_request(self.uri + '/createUploadSession', 'POST', {
            "item": {"@microsoft.graph.conflictBehavior": conflict_behavior}
        }, fail_silently=fail_silently)

    # 创建文件分享链接
    # https://docs.microsoft.com/zh-cn/onedrive/developer/rest-api/api/driveitem_createlink?view=odsp-graph-online
    def create_link(self, fail_silently=False) -> requests.Response:
        return onedrive_http_request(self.uri + '/createLink', 'POST', {
            "type": "view",
            "scope": "anonymous"
        }, fail_silently=fail_silently)

    # 创建分享链接后改写链接，使其可以被（重定向后）下载
    def get_download_link(self, fail_silently=False) -> str:
        response = self.create_link(fail_silently=fail_silently)
        share_link = response.json()['link']['webUrl']
        download_link = share_link.split('?')[0] + '?download=1'
        return download_link
