from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from cloud.onedrive import onedrive_temp_directory
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
            return Response({"detail":"需要参数 filename"}, status=status.HTTP_400_BAD_REQUEST)
        # 先将文件上传至 temp 文件夹，在 done 时再将文件移动至对应位置
        response = onedrive_temp_directory.find_file_by_path(filename).create_upload_session('replace')
        return Response(response.content, status=status.HTTP_200_OK)
