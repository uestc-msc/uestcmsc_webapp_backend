
from django.shortcuts import redirect
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from config import FRONTEND_URL
from cloud.onedrive.api.auth import OnedriveAuthentication
from utils.swagger import *


@swagger_auto_schema(
    method='GET',
    operation_summary='登录 Onedrive 账号',
    operation_description='重定向到登录 Onedrive 的网址',
    responses={301: OnedriveAuthentication.login_uri(), 200: Schema_None}
)
@api_view(['GET'])
def onedrive_login(request: Request):
    return redirect(OnedriveAuthentication.login_uri(), permanent=True)


@swagger_auto_schema(
    method='GET',
    operation_summary='Onedrive 登录成功后重定向网址',
    operation_description='用于截取登录成功的 `auth_token`，没事别 xjb 打开这个',
    responses={302: FRONTEND_URL + '/cloud/status/', 200: Schema_None}
)
@api_view(['GET'])
def onedrive_login_callback(request: Request):
    auth_code = request.GET.get('code', '')
    if auth_code == '':
        return Response("都说了叫你没事别 xjb 打开这个", status=400)
    else:
        OnedriveAuthentication.grant_access_token(auth_code)
        return redirect(FRONTEND_URL + '/cloud/status/')
