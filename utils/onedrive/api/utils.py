from typing import Dict, Union, List

import requests
from django.core.cache import cache

from utils.onedrive.auth import onedrive_access_token_cache_name

base_url = 'https://graph.microsoft.com/v1.0'


# path 应以 '/' 开头，且不应以 '/' 结尾
def validate_path(path: str) -> str:
    if path.endswith('/'):
        path = path[0:-1]
    if not path.startswith('/'):
        path = '/' + path
    return path


def onedrive_http_request(uri: str,
                          method='GET',
                          json: Dict = None,
                          data=None,
                          content_type='application/json',
                          extra_headers: Dict = None,
                          **kwargs) -> requests.Response:
    access_code = cache.get(onedrive_access_token_cache_name, '')
    if access_code == '':
        response = requests.Response()
        response.status_code = 401
        return response
    headers = extra_headers.copy() if extra_headers else {}
    headers['Content-Type'] = content_type
    headers['Authorization'] = f'bearer {access_code}'
    if data:
        kwargs['data'] = data
    if json:
        kwargs['json'] = json
    return requests.request(method=method, url=base_url + uri, headers=headers, **kwargs)
