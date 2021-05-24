from typing import Optional

from django.core.cache import cache

__onedrive_access_token_name = 'onedrive__access_token'
__onedrive_refresh_token_name = 'onedrive__refresh_token'
__onedrive_file_temp_link_prefix = 'onedrive__file_temp_link__'


def get_access_token() -> Optional[str]:
    """
    从缓存获取 access_token，不存在则返回 None
    """
    return cache.get(__onedrive_access_token_name, None)


def set_access_token(value: str, timeout: int = None):
    """
    设置 access_token 和缓存时限（单位：秒）
    """
    cache.set(__onedrive_access_token_name, value, timeout=timeout)


def get_refresh_token() -> Optional[str]:
    """
    从缓存获取 refresh_token，不存在则返回 None
    """
    return cache.get(__onedrive_refresh_token_name, None)


def set_refresh_token(value: str, timeout: int = None):
    """
    设置 refresh_token 和缓存时限（单位：秒）
    """
    cache.set(__onedrive_refresh_token_name, value, timeout=timeout)


def get_onedrive_file_temp_link_from_cache(id: str) -> Optional[str]:
    """
    从缓存获取文件临时下载链接，不存在则返回 None
    """
    return cache.get(__onedrive_file_temp_link_prefix + id, None)


def set_onedrive_file_temp_link_to_cache(id: str, link: str, timeout: int = None):
    """
    设置文件临时下载链接和缓存时限（单位：秒）
    """
    cache.set(__onedrive_file_temp_link_prefix + id, link, timeout=timeout)
