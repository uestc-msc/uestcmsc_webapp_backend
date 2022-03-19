import os
from typing import TypeVar, Union

from dotenv import dotenv_values

dot_environ = dotenv_values('.env')
T = TypeVar('T')


# 应用名称和版本号
APP_NAME = "阮薇薇点名啦"
API_VERSION = "v0.3.0 beta"


# get env var from:
# 1. os.environ
# 2. '.env' file
# 3. default value
def env_or(default: T, key: str) -> Union[T, str]:
    return os.environ.get(key) or dot_environ.get(key) or default


# get boolean type env var
def env_or_bool(default: bool, key: str) -> bool:
    return env_or(str(default), key).upper() == 'TRUE'


DJANGO_SECRET_KEY = env_or("", "DJANGO_SECRET_KEY")
DJANGO_DEBUGGING_MODE = env_or_bool(False, "DJANGO_DEBUGGING_MODE")
DJANGO_SERVER_HOSTNAME = 'api.uestc-msc.com'

# 前端的 URL，用于生成签到二维码、邮箱网址等等
FRONTEND_URL = "https://app.uestc-msc.com"
FRONTEND_TRUSTED_ORIGINS = ['.uestc-msc.com']

# 数据库的相关配置
MYSQL_HOST = env_or("127.0.0.1", "MYSQL_HOST")
MYSQL_PORT = env_or("3306", "MYSQL_PORT")
MYSQL_USERNAME = env_or("root", "MYSQL_USERNAME")
MYSQL_PASSWORD = env_or("123456", "MYSQL_PASSWORD")
MYSQL_DATABASE = env_or("mysql", "MYSQL_DATABASE")
REDIS_HOST = env_or("redis://127.0.0.1:6379/1", "REDIS_HOST")
REDIS_PASSWORD = env_or("123456", "REDIS_PASSWORD")

# Gravatar 镜像站，为 None 表示不使用
# GRAVATAR_MIRROR = "https://dn-qiniu-avatar.qbox.me/avatar/"   # 七牛的延迟最低，但不支持 params
GRAVATAR_MIRROR = "https://sdn.geekzu.org/avatar/"
USER_DEFAULT_AVATAR = "https://app.uestc-msc.com/img/ruanweiwei.jpg"

# 邮箱（用于发送验证邮件等）的相关配置
MAILBOX_HOST = env_or("", "MAILBOX_HOST")
MAILBOX_PORT = env_or("", "MAILBOX_PORT")
MAILBOX_EMAIL = env_or("", "MAILBOX_EMAIL")
MAILBOX_PASSWORD = env_or("", "MAILBOX_PASSWORD")
MAILBOX_USE_TLS = env_or_bool(True, "MAILBOX_USE_TLS")
MAILBOX_USE_SSL = env_or_bool(False, "MAILBOX_USE_SSL")


MANAGERS = [('小灰晖', 'lyh543@outlook.com')]


# OneDrive 部分配置
ONEDRIVE_CLIENT_ID = env_or("", "ONEDRIVE_CLIENT_ID")
ONEDRIVE_CLIENT_SECRET = env_or("", "ONEDRIVE_CLIENT_SECRET")
