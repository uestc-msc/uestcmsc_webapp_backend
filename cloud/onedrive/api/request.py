from typing import Dict

import requests
from cloud.onedrive.auth import OnedriveAuthentication, OnedriveUnavailableException
from cloud.onedrive.cache import get_access_token

base_url = 'https://graph.microsoft.com/v1.0'


# 纠正 path 语法，使其以 '/' 开头，且不以 '/' 结尾
def validate_path(path: str) -> str:
    if path.endswith('/'):
        path = path[0:-1]
    if not path.startswith('/'):
        path = '/' + path
    return path


# 向 Onedrive 服务器发起请求
# fail_silently 为 true 时请求失败不会抛异常
def onedrive_http_request(uri: str,
                          method='GET',
                          json: Dict = None,
                          data=None,
                          content_type='application/json',
                          extra_headers: Dict = None,
                          fail_silently=False,
                          **kwargs) -> requests.Response:
    access_code = get_access_token()
    if access_code is None:
        # 尝试用 refresh_token 刷新 access_token
        OnedriveAuthentication.refresh_access_token()
        # 如果再次失败说明 refresh_token 失效，需要重新登录
        access_code = get_access_token()
        if access_code is None:
            raise OnedriveUnavailableException

    headers = extra_headers.copy() if extra_headers else {}
    headers['Content-Type'] = content_type
    headers['Authorization'] = f'bearer {access_code}'
    if data:
        kwargs['data'] = data
    if json:
        kwargs['json'] = json
    response = requests.request(method=method, url=base_url + uri, headers=headers, **kwargs)
    if not response.ok and not fail_silently:
        raise OnedriveUnavailableException(response=response)
    return response
