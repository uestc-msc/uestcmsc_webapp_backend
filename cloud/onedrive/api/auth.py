import logging

import requests
from rest_framework.exceptions import APIException

import config
from cloud.onedrive.api.cache import get_refresh_token, set_access_token, set_refresh_token
from cloud.onedrive.api.request import catchConnectionError
from uestcmsc_webapp_backend.settings import DEBUG
from utils.mail import send_system_alert_mail_to_managers


logger = logging.getLogger(__name__)


class OnedriveAuthentication:
    client_id = config.ONEDRIVE_CLIENT_ID
    client_secret = config.ONEDRIVE_CLIENT_SECRET
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    scope = "Files.ReadWrite offline_access"

    redirect_path = '/api/cloud/login_callback/'
    _origin = 'http://localhost:8000' if DEBUG else f'https://{config.DJANGO_SERVER_HOSTNAME}'
    redirect_uri = _origin + redirect_path

    @classmethod
    def generate_errormsg(cls, event: str, response: requests.Response) -> str:
        return f'{event}，状态码 {response.status_code}，详细信息：{response.json()}'

    # 登录页面需要用户自行访问，于是这里只负责生成 uri，登录授权成功后跳转到指定链接，链接中 params 即是 auth_token
    # 为方便使用，/cloud/login/ 页面将被重定向到该 uri（见 /cloud/views.py）
    @classmethod
    def login_uri(cls):
        return f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id={cls.client_id}" \
               f"&scope={cls.scope}&response_type=code&redirect_uri={cls.redirect_uri}"

    # 拿到 auth_token 后，后端请求获取 access_token 和 refresh_token
    @classmethod
    @catchConnectionError
    def grant_access_token(cls, auth_token=''):
        if auth_token == '':
            raise ValueError("onedrive.auth_token is ''")
        response = requests.post('https://login.microsoftonline.com/common/oauth2/v2.0/token',
                                 data={'client_id': cls.client_id,
                                       'redirect_uri': cls.redirect_uri,
                                       'client_secret': cls.client_secret,
                                       'code': auth_token,
                                       'grant_type': 'authorization_code'},
                                 headers=cls.headers)
        if response.status_code == 200:
            cls._save_token(response)
            from cloud.onedrive import initialize_onedrive
            initialize_onedrive()
        else:
            error_info = cls.generate_errormsg('获取 Onedrive Access Token 失败', response)
            logger.error(error_info)

    # access_token 即将过期，用 refresh_token 获取新的 access_token 和 refresh_token
    @classmethod
    @catchConnectionError
    def refresh_access_token(cls, refresh_token=None):
        if refresh_token is None:
            refresh_token = get_refresh_token()
            if refresh_token is None:
                return  # 如果本身没有 refresh_token，就不提醒管理员了；删除 refresh_token 已经提醒过了
        response = requests.post('https://login.microsoftonline.com/common/oauth2/v2.0/token',
                                 data={'client_id': cls.client_id,
                                       'redirect_uri': cls.redirect_uri,
                                       'client_secret': cls.client_secret,
                                       'refresh_token': refresh_token,
                                       'grant_type': 'refresh_token'},
                                 headers=cls.headers)
        if response.status_code == 200:
            cls._save_token(response)
        else:
            error_info = cls.generate_errormsg('刷新 Onedrive Access Token 失败', response)
            logger.error(error_info)
            send_system_alert_mail_to_managers(error_info)
            return

    @classmethod
    def _save_token(cls, response: requests.Response):
        response_json = response.json()
        access_token = response_json.get('access_token', None)
        access_token_expires_in = response_json.get('expires_in', 3600)
        refresh_token = response_json.get('refresh_token', None)
        if access_token is None or refresh_token is None:
            error_info = cls.generate_errormsg('获取的 Onedrive Access Token 或 Refresh Token 为 None', response)
            logger.error(error_info)
            send_system_alert_mail_to_managers(error_info)
            return
        else:
            set_access_token(access_token, timeout=access_token_expires_in)
            set_refresh_token(refresh_token, timeout=None)
            logger.info('Onedrive 获取 Access Token 和 Refresh Token 成功')
            return


class OnedriveUnavailableException(APIException):
    status_code = 503
    default_detail = 'Onedrive 服务错误，请稍后再试或询问管理员。'
    default_code = 'service_unavailable'
