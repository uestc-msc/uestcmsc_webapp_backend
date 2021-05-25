from typing import Optional
from django.core.cache import cache

_onedrive_access_token_name = 'onedrive__access_token'
onedrive_refresh_token_name = 'onedrive__refresh_token'
onedrive_file_link_prefix = 'onedrive__file_link_'


class CacheMeta(type):
    @property
    def onedrive_access_token(cls) -> Optional[str]:
        """
        从缓存获取 access_token，不存在则返回 None
        """
        return cache.get(_onedrive_access_token_name, None)

    @onedrive_access_token.setter
    def onedrive_access_token(cls, value: str):
        """
        设置 access_token 和缓存时限（单位：秒）
        """
        cache.set(_onedrive_access_token_name, value, timeout=3600)

    @property
    def onedrive_refresh_token(cls) -> Optional[str]:
        """
        从缓存获取 refresh_token，不存在则返回 None
        """
        return cache.get(onedrive_refresh_token_name, None)

    @onedrive_refresh_token.setter
    def onedrive_refresh_token(cls, value: str):
        """
        设置 refresh_token 和缓存时限（单位：秒）
        """
        cache.set(onedrive_refresh_token_name, value, timeout=None)

    class __OnedriveFileLinkCache:
        def __getitem__(self, key):
            """
            从缓存获取文件临时下载链接，不存在则返回 None
            """
            return cache.get(onedrive_file_link_prefix + key, None)

        def __setitem__(self, key, value):
            """
            设置文件临时下载链接和缓存时限（单位：秒）
            """
            cache.set(onedrive_file_link_prefix + key, value, timeout=300)

    onedrive_file_temp_link = __OnedriveFileLinkCache()


class Cache(metaclass=CacheMeta):
    pass
