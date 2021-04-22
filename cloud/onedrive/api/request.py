import functools
import logging
import urllib.parse
from typing import Dict, Callable

import requests

base_url = 'https://graph.microsoft.com/v1.0'
logger = logging.getLogger(__name__)


# 纠正 path 语法，使其以 '/' 开头，且不以 '/' 结尾
# 然后 url encode:
# https://docs.microsoft.com/zh-cn/onedrive/developer/rest-api/concepts/addressing-driveitems#encoding-characters
def validate_path(path: str) -> str:
    if path.endswith('/'):
        path = path[0:-1]
    if not path.startswith('/'):
        path = '/' + path
    return urllib.parse.quote(path)     # url encode


def log_onedrive_error(response: requests.Response):
    logger.error(f"Onedrive 请求失败：{response.request.url}, "
                 f"status_code={response.status_code}, "
                 f"response={response.content.decode()}", stack_info=True)


def catchConnectionError(func: Callable):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ConnectionError:
            logger.error("无法连接到 Onedrive", stack_info=True)
            from cloud.onedrive.api.auth import OnedriveUnavailableException
            raise OnedriveUnavailableException
    return wrapper


# 向 Onedrive 服务器发起请求
# fail_silently 为 true 时响应不为 2xx 时不会抛异常
# 连接错误一定会抛出异常
@catchConnectionError
def onedrive_http_request(uri: str,
                          method='GET',
                          json: Dict = None,
                          data=None,
                          content_type='application/json',
                          extra_headers: Dict = None,
                          fail_silently=False,
                          **kwargs) -> requests.Response:
    from cloud.onedrive.api.auth import OnedriveAuthentication, OnedriveUnavailableException
    from cloud.onedrive.api.cache import get_access_token
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
        log_onedrive_error(response)
        raise OnedriveUnavailableException
    return response
