from django.core.cache import cache

__onedrive_access_token_name = 'onedrive__access_token'
__onedrive_refresh_token_name = 'onedrive__refresh_token'


# 从缓存获取 access_token，不存在则返回 None
def get_access_token() -> str:
    return cache.get(__onedrive_access_token_name, None)


# 从缓存获取 refresh_token，不存在则返回 None
def get_refresh_token() -> str:
    return cache.get(__onedrive_refresh_token_name, None)


# 设置 access_token 和缓存时限（单位：秒）
def set_access_token(value: str, timeout: int = None):
    cache.set(__onedrive_access_token_name, value, timeout=timeout)


# 设置 refresh_token 和缓存时限（单位：秒）
def set_refresh_token(value: str, timeout: int = None):
    cache.set(__onedrive_refresh_token_name, value, timeout=timeout)