from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import redirect
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.response import Response

from cloud.onedrive import onedrive
from config import FRONTEND_URL


@swagger_auto_schema(
    method='GET',
    operation_summary='登录 Onedrive 账号',
    operation_description='重定向到登录 Onedrive 的网址'
)
@api_view(['GET'])
def onedrive_login(request: WSGIRequest):
    return redirect(onedrive.login_uri())


@swagger_auto_schema(
    method='GET',
    operation_summary='Onedrive 登录成功后重定向网址',
    operation_description='没事别 xjb 打开这个'

)
@api_view(['GET'])
def onedrive_login_callback(request: WSGIRequest):
    auth_code = request.GET.get('code', '')
    if auth_code == '':
        return Response("都说了叫你没事别 xjb 打开这个啊", status=400)
    else:
        onedrive.grant_access_token(auth_code)
        return redirect(FRONTEND_URL + '/cloud/status/')


@swagger_auto_schema(
    method='GET',
    operation_summary='Onedrive 状态',
    operation_description=''

)
@api_view(['GET'])
def onedrive_status(request: WSGIRequest) -> Response:
    pass