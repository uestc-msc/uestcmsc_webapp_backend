# config.py 包含了密码等信息，不应当公开！！！！！
# 务必把 config.py 加入 .gitignore!

# DJANGO_SECRET_KEY，见 https://docs.djangoproject.com/en/3.1/ref/settings/#std:setting-SECRET_KEY
DJANGO_SECRET_KEY = "23333333333333333333333333333333333333333333333333"
DJANGO_DEBUGGING_MODE = True
DJANGO_SERVER_HOSTNAME = 'api.uestc-msc.com'

# 前端的 URL，用于生成签到二维码、邮箱网址等等
FRONTEND_URL = "https://app.uestc-msc.com"
FRONTEND_TRUSTED_ORIGINS = ['.uestc-msc.com']

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

# MANAGERS，系统错误（如 Onedrive 需要登录）时会发送邮件给这些人
MANAGERS = [('小灰晖', 'lyh543@outlook.com')]

# OneDrive 部分配置
ONEDRIVE_CLIENT_ID = "815e752f-945e-11eb-8b82-8cc84bbcb0e4"
ONEDRIVE_CLIENT_SECRET = "1234567890!#$%^&*()qwertyuio"
