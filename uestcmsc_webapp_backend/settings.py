"""
Django settings for uestcmsc_webapp_backend project.

Generated by 'django-admin startproject' using Django 3.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
from pathlib import Path
from config import *
import subprocess

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret file_id used in production secret!
SECRET_KEY = DJANGO_SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = DJANGO_DEBUGGING_MODE

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver', DJANGO_SERVER_HOSTNAME]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 'django_crontab',
    'corsheaders',
    'rest_framework',
    'drf_yasg',  # API document generation

    'accounts.apps.AccountsConfig',
    'activities.apps.ActivitiesConfig',
    'cloud.apps.CloudConfig',
    'activities_comments.apps.ActivitiesCommentsConfig',
    'activities_files.apps.ActivitiesFilesConfig',
    'activities_links.apps.ActivitiesLinksConfig',
    'activities_photos.apps.ActivitiesPhotosConfig',
    'activities_tags.apps.ActivitiesTagsConfig',
    'users.apps.UsersConfig',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # CORS 中间件，需注意与其他中间件顺序，这里放在最前面即可
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'uestcmsc_webapp_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'uestcmsc_webapp_backend.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': MYSQL_DATABASE,
        'USER': MYSQL_USERNAME,
        'PASSWORD': MYSQL_PASSWORD,
        'HOST': MYSQL_HOST,
        'PORT': MYSQL_PORT,
        'OPTIONS': {'charset': 'utf8mb4'}, # 支持 emoji
    }
}
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Caches

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_HOST,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": REDIS_PASSWORD
        }
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = False

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, '.static')  # 应在 Nginx/Caddy 中提供这个文件夹
STATIC_URL = '/api/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]

# Settings about email
EMAIL_HOST = MAILBOX_HOST
EMAIL_PORT = MAILBOX_PORT
EMAIL_HOST_USER = MAILBOX_EMAIL
EMAIL_HOST_PASSWORD = MAILBOX_PASSWORD
EMAIL_USE_TLS = MAILBOX_USE_TLS
EMAIL_USE_SSL = MAILBOX_USE_SSL

# Send System Alert Email to managers
MANAGERS = MANAGERS

# Django crontab (not available for windows)
# CRONJOBS = [
#     ('*/40 * * * *', 'cloud.onedrive.refresh_access_token') # 目前采用使用时刷新 access_token 替代定时刷新
# ]

# Auto Append Slash
APPEND_SLASH = True

# settings about Swagger (Document Generator)
SWAGGER_SETTINGS = {
    'DEFAULT_MODEL_RENDERING': 'example'
}

# CORS extra_headers
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = (
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
    'VIEW',
)
CORS_ALLOW_HEADERS = (
    'XMLHttpRequest',
    'X_FILENAME',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'Pragma',
)

# CSRF & Session Cookies
CSRF_USE_SESSIONS = False
if not DEBUG:
    CSRF_COOKIE_DOMAIN = FRONTEND_TRUSTED_ORIGINS[0]
    SESSION_COOKIE_DOMAIN = FRONTEND_TRUSTED_ORIGINS[0]
    CSRF_TRUSTED_ORIGINS = FRONTEND_TRUSTED_ORIGINS
