from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from activities.models import Activity, ActivityOnedriveFolder
from utils.log import log_error
from utils.onedrive import activity_directory, temp_directory
from utils.onedrive.auth import OnedriveUnavailableException
from utils.permissions import IsPresenterOrAdminOrReadOnly, IsAuthenticated

from utils.swagger import *


@method_decorator(name="post", decorator=swagger_auto_schema(
    operation_summary='向沙龙上传文件',
    operation_description='如果成功，返回上传链接，使用方法参考 [Onedrive 文档](https://docs.microsoft.com/zh-cn/'
                          'onedrive/developer/rest-api/api/driveitem_createuploadsession?'
                          'view=odsp-graph-online#response)\n'
                          '注：需要登录，否则返回 403\n'
                          '注 2：上传完成后还需要调用完成文件上传的接口',
    request_body=Schema_object(Schema_filename),
    responses={200: Schema_None}
))
@method_decorator(name="delete", decorator=swagger_auto_schema(
    operation_summary='删除沙龙文件',
    operation_description='删除沙龙文件，成功返回 204\n'
                          '文件不存在或不在该沙龙下，返回 404\n'
                          '注：需要是沙龙演讲者或管理员，否则返回 403',
    request_body=Schema_object(Schema_file_id, Schema_filetype)
))
class OnedriveFileView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request: Request) -> Response:
        filename = request.data.get('filename', None)
        if filename is None:
            return Response({"detail":"需要参数 filename"}, status=status.HTTP_400_BAD_REQUEST)
        # 先将文件上传至 temp 文件夹，在 done 时再将文件移动至对应位置
        response = temp_directory.find_file_by_path(filename).create_upload_session('replace')
        return Response(response.content, status=status.HTTP_200_OK)

    def delete(self, request: Request) -> Response:
        pass


def onedrive_file_upload_done(request: Request) -> Response:
    activity = get_object_or_404(Activity, id=id)
    self.check_object_permissions(request, activity)
    if hasattr(activity, 'folder'):
        folder_id = activity.folder.id
    else:
        response = activity_directory.create_directory(activity.title)
        folder_id = response.json()['id']
        ActivityOnedriveFolder.objects.create(id=folder_id, activity=activity)
    activity_directory.find_file_by_id(folder_id).find_file_by_path(filename).create_upload_session()