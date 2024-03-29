import functools
import logging
import urllib.parse
from typing import Dict, Callable
import aiohttp
import requests

from utils.cache import Cache

base_url = 'https://graph.microsoft.com/v1.0'
logger = logging.getLogger(__name__)


def validate_path(path: str) -> str:
    """
    纠正 path 语法，使其以 '/' 开头，且不以 '/' 结尾
    然后 url encode:
    https://docs.microsoft.com/zh-cn/graph/concepts/addressing-driveitems#encoding-characters
    """
    if path.endswith('/'):
        path = path[0:-1]
    if not path.startswith('/'):
        path = '/' + path
    return urllib.parse.quote(path)  # url encode


def log_onedrive_error(response: requests.Response):
    """
    记录 onedrive 请求错误
    """
    logger.error(f"Onedrive 请求失败：{response.request.url}, "
                 f"status_code={response.status_code}, "
                 f"response={response.content.decode()}")


async def log_async_onedrive_error(response: aiohttp.ClientResponse):
    """
    记录 onedrive 请求错误
    """
    logger.error(f"Onedrive 异步失败：{response.request_info.url}, "
                 f"status_code={response.status}, "
                 f"response={await response.text()}")


def catchConnectionError(func: Callable):
    """
    在不加捕获的情况下，发生 ConnectionError 会抛出 500 错误
    该装饰器装饰后的函数会捕获该错误，然后返回 503 OnedriveUnavailableException
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ConnectionError:
            logger.error("无法连接到 Onedrive", stack_info=True)
            from cloud.onedrive.api.auth import OnedriveUnavailableException
            raise OnedriveUnavailableException

    return wrapper


def _prepare_onedrive_http_request(
        json: Dict = None,
        data=None,
        content_type='application/json',
        extra_headers: Dict = None,
        *args,
        **kwargs) -> [Dict, Dict]:
    """
    准备请求的报头
    """
    from cloud.onedrive.api.auth import OnedriveAuthentication, OnedriveUnavailableException
    access_token = Cache.onedrive_access_token
    if access_token is None:
        # 尝试用 refresh_token 刷新 access_token
        OnedriveAuthentication.refresh_access_token()
        # 如果再次失败说明 refresh_token 失效，需要重新登录
        access_token = Cache.onedrive_access_token
        if access_token is None:
            raise OnedriveUnavailableException
    # 准备 headers 和其他 requests 参数
    headers = extra_headers.copy() if extra_headers else {}
    headers['Content-Type'] = content_type
    headers['Authorization'] = f'bearer {access_token}'
    if data:
        kwargs['data'] = data
    if json:
        kwargs['json'] = json
    return headers, kwargs


def onedrive_http_request(
        uri: str,
        method='GET',
        json: Dict = None,
        data=None,
        content_type='application/json',
        extra_headers: Dict = None,
        fail_silently=False,
        try_times=5,
        *args,
        **kwargs) -> requests.Response:
    """
    向 Onedrive 服务器发起请求
    fail_silently 为 true 时响应不为 2xx 时不会抛异常
    """
    headers, kwargs = _prepare_onedrive_http_request(json, data, content_type, extra_headers, *args, **kwargs)
    for i in range(try_times):
        try:
            response = requests.request(method=method, url=base_url + uri, headers=headers, **kwargs)
            if response.ok or fail_silently:
                return response
            log_onedrive_error(response)
        except ConnectionError:
            continue
    from cloud.onedrive.api.auth import OnedriveUnavailableException
    raise OnedriveUnavailableException


async def async_onedrive_http_request(
        uri: str,
        method='GET',
        json: Dict = None,
        data=None,
        content_type='application/json',
        extra_headers: Dict = None,
        fail_silently=False,
        try_times=5,
        *args,
        **kwargs) -> aiohttp.ClientResponse:
    """
    向 Onedrive 服务器异步发起请求
    fail_silently 为 true 时响应不为 2xx 时不会抛异常
    连接错误一定会抛出异常
    """
    headers, kwargs = _prepare_onedrive_http_request(json, data, content_type, extra_headers, *args, **kwargs)
    async with aiohttp.ClientSession() as session:
        for i in range(try_times):
            try:
                async with session.request(method=method, url=base_url + uri, headers=headers, **kwargs) as response:
                    if response.ok or fail_silently:
                        return response
                    await log_async_onedrive_error(response)
            except ConnectionError:
                continue
    from cloud.onedrive.api.auth import OnedriveUnavailableException
    raise OnedriveUnavailableException
