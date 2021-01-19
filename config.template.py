# config.py 包含了非常重要的信息，不应该dang开源！！！！！
# 务必把 config.py 加入 .gitignore

# 应用名称和版本号
APP_NAME = "阮薇薇点名啦"
API_VERSION = "v0.1.0 α"

# DJANGO_SECRET_KEY，见 https://docs.djangoproject.com/en/3.1/ref/settings/#std:setting-SECRET_KEY
DJANGO_SECRET_KEY = "23333333333333333333333333333333333333333333333333"
DJANGO_DEBUGGING_MODE = True
DJANGO_SERVER_HOSTNAME = ['localhost', '127.0.0.1', 'app.uestc-msc.com']

# 数据库的相关配置
MYSQL_HOST = "127.0.0.1"
MYSQL_PORT = "3306"
MYSQL_USERNAME = "root"
MYSQL_PASSWORD = "testtest"
MYSQL_DATABASE = "uestcmsc_webapp"

# 邮箱（用于发送验证邮件等）的相关配置
MAILBOX_HOST = "smtp.office365.com"
MAILBOX_PORT = "587"
MAILBOX_EMAIL = "example@outlook.com"
MAILBOX_PASSWORD = "password"
MAILBOX_USE_TLS = True
MAILBOX_USE_SSL = False

# 前端的 URL，用于生成签到二维码、邮箱网址等等
FRONTEND_URL = "https://app.uestc-msc.com"
