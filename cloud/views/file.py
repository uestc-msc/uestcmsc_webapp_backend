from typing import Optional

from asgiref.sync import sync_to_async
from django.core.cache import cache
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from cloud.onedrive import onedrive_temp_directory
from cloud.onedrive.api import onedrive_drive
from utils.asynchronous import thread_insensitive_sync_to_async
from utils.permissions import IsAuthenticated
from utils.swagger import *


@method_decorator(name="post", decorator=swagger_auto_schema(
    operation_summary='创建文件上传会话',
    operation_description='响应报文和 [Onedrive 文档](https://docs.microsoft.com/zh-cn/'
                          'onedrive/developer/rest-api/api/driveitem_createuploadsession?'
                          'view=odsp-graph-online#response) 相同，包含临时上传链接\n'
                          '注：需要登录，否则返回 403\n'
                          '注 2：前端需按 Onedrive 文档所示方法，将文件上传至链接。上传完成后还需要调用对应文件上传完成的接口，否则文件将在 24 小时内被清除',
    request_body=Schema_object(Schema_filename),
    responses={200: Schema_None}
))
class OnedriveFileView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request: Request) -> Response:
        filename = request.data.get('filename', None)
        if filename is None:
            return Response({"detail": "需要参数 filename"}, status=status.HTTP_400_BAD_REQUEST)
        user_id = request.user.id
        user_directory = f'user{user_id}'
        # 使用 /temp/user{id}/filename 作为上传路径。避免上传冲突
        onedrive_temp_directory.create_directory(user_directory, fail_silently=True)
        # 要求前端先将文件上传至 temp 文件夹，完成后再发对应请求，后端将文件移动至对应位置
        response = onedrive_temp_directory \
            .find_file_by_path(f"/{user_directory}/{filename}") \
            .create_upload_session('replace')
        return Response(response.content, status=status.HTTP_200_OK)


__onedrive_file_temp_link_prefix = 'onedrive__file_temp_link__'


def get_onedrive_file_temp_link_from_cache(id: str) -> Optional[str]:
    """
    从缓存获取文件临时下载链接，不存在则返回 None
    """
    return cache.get(__onedrive_file_temp_link_prefix + id, None)


def set_onedrive_file_temp_link_to_cache(id: str, link: str, timeout: int = None):
    """
    设置文件临时下载链接和缓存时限（单位：秒）
    """
    cache.set(__onedrive_file_temp_link_prefix + id, link, timeout=timeout)


@swagger_auto_schema(
    operation_summary='获取文件下载链接',
    operation_description='~~本 API 只是调用 Onedrive API 后的转发机器~~\n'
                          '如果 id 对应的文件不存在，返回 404\n'
                          '如果 id 对应的文件存在，响应报文为 `302 Found`，`Location` 为一个下载 URL。\n'
                          '该 URL 仅在较短的一段时间 （几分钟后）内有效，不需要认证即可下载。\n'
                          '注：为减少对 Onedrive API 的调用，本 API 对 file_id 进行 300s 的缓存，如获取内容未刷新，请稍后再试',
    responses={302: 'Found', 200: Schema_None}
)
@thread_insensitive_sync_to_async
def onedrive_file_download_view(request: Request, id: str) -> HttpResponse:
    file_link = get_onedrive_file_temp_link_from_cache(id)
    if not file_link:
        onedrive_response = onedrive_drive.find_file_by_id(id).get_download_link_temp(fail_silently=True)
        if onedrive_response.status_code != 302:
            return HttpResponse(onedrive_response.content, status=onedrive_response.status_code)
        file_link = onedrive_response.headers['Location']
        set_onedrive_file_temp_link_to_cache(id, file_link, 300)  # 设五分钟后过期
    return HttpResponse(headers={'Location': file_link}, status=302)
