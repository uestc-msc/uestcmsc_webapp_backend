import json
import os

import requests
from django.core.cache import cache
from requests import Response

import config
from uestcmsc_webapp_backend.settings import DEBUG
from utils.asynchronous import asynchronous
from utils.log import log_error, log_info
from utils.mail import send_system_alert_mail_to_managers

if DEBUG:
    os.environ['NO_PROXY'] = 'login.microsoftonline.com'


class Onedrive():
    def __init__(self):
        if config.ONEDRIVE_CLIENT_ID == '':
            raise ValueError("ONEDRIVE_CLIENT_ID is ''")
        if config.ONEDRIVE_CLIENT_SECRET == '':
            raise ValueError("ONEDRIVE_CLIENT_SECRET is ''")

        self.client_id = config.ONEDRIVE_CLIENT_ID
        self.client_secret = config.ONEDRIVE_CLIENT_SECRET
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        self.scope = "Files.ReadWrite offline_access"
        self.access_token_cache_name = 'onedrive__access_token'
        self.refresh_token_cache_name = 'onedrive__refresh_token'
        self.redirect_path = '/api/cloud/login_callback/'
        host = 'http://localhost:8000' if DEBUG else f'https://{config.DJANGO_SERVER_HOSTNAME}'
        self.redirect_uri = host + self.redirect_path

    def generate_errormsg(self, event: str, response: Response) -> str:
        return f'{event}，状态码 {response.status_code}，详细信息：{json.loads(response.content)}'

    # 登录页面需要用户自行访问，于是这里只负责生成 uri，登录授权成功后跳转到指定链接，链接中 params 即是 auth_token
    def login_uri(self):
        return f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id={self.client_id}" \
               f"&scope={self.scope}&response_type=code&redirect_uri={self.redirect_uri}"

    # 拿到 auth_token 后，后端请求获取 access_token 和 refresh_token
    @asynchronous
    def grant_access_token(self, auth_token=''):
        if auth_token == '':
            raise ValueError("onedrive.auth_token is ''")
        response = requests.post('https://login.microsoftonline.com/common/oauth2/v2.0/token',
                                 data={'client_id': self.client_id,
                                       'redirect_uri': self.redirect_uri,
                                       'client_secret': self.client_secret,
                                       'code': auth_token,
                                       'grant_type': 'authorization_code'},
                                 headers=self.headers)
        if response.status_code == 200:
            self._save_access_token(response)
        else:
            log_error(self.generate_errormsg('获取 Onedrive Access Token 失败', response))
            return

    # access_token 即将过期，用 refresh_token 获取新的 acess_token 和 refresh_token
    def refresh_access_token(self, refresh_token=None):
        if refresh_token is None:
            refresh_token = cache.get(self.refresh_token_cache_name, None)
            if refresh_token is None:
                return # 如果本身没有 refresh_token，就不提醒管理员了；删除 refresh_token 已经提醒过了
        response = requests.post('https://login.microsoftonline.com/common/oauth2/v2.0/token',
                                 data={'client_id': self.client_id,
                                       'redirect_uri': self.redirect_uri,
                                       'client_secret': self.client_secret,
                                       'refresh_token': refresh_token,
                                       'grant_type': 'refresh_token'},
                                 headers=self.headers)
        if response.status_code == 200:
            self._save_access_token(response)
        else:
            error_info = self.generate_errormsg('刷新 Onedrive Access Token 失败', response)
            log_error(error_info)
            send_system_alert_mail_to_managers(error_info)
            return

    def _save_access_token(self, response: Response):
        response_json = json.loads(response.content)
        access_token = response_json.get('access_token', None)
        access_token_expires_in = response_json.get('expires_in', 3600)
        refresh_token = response_json.get('refresh_token', None)
        if access_token is None or refresh_token is None:
            error_info = self.generate_errormsg('获取的 Onedrive Access Token 或 Refresh Token 为 None', response)
            log_error(error_info)
            send_system_alert_mail_to_managers(error_info)
            return
        else:
            cache.set(self.access_token_cache_name, access_token, timeout=access_token_expires_in)
            cache.set(self.refresh_token_cache_name, refresh_token, timeout=None)
            log_info('Onedrive 获取 Access Token 和 Refresh Token 成功')


onedrive = Onedrive()
