from django.core.handlers.wsgi import WSGIRequest
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from activities.models import Activity
from utils.onedrive.auth import OnedriveUnavailableException
from utils.permissions import IsPresenterOrAdminOrReadOnly

from utils.swagger import *

@method_decorator(name="post", decorator=swagger_auto_schema(
    operation_summary='向沙龙上传文件',
    operation_description='如果成功，返回上传链接，使用方法参考 [Onedrive 文档](https://docs.microsoft.com/zh-cn/'
                          'onedrive/developer/rest-api/api/driveitem_createuploadsession?'
                          'view=odsp-graph-online#response)\n'
                          '注：需要是沙龙演讲者或管理员，否则返回 403\n'
                          '注 2：上传完成后还需要调用完成文件上传的接口',
    request_body=Schema_object(Schema_activity_id),
))
@method_decorator(name="delete", decorator=swagger_auto_schema(
    operation_summary='删除沙龙',
    operation_description='删除沙龙文件，成功返回 204\n'
                          '文件不存在或不在该沙龙下，返回 404\n'
                          '注：需要是沙龙演讲者或管理员，否则返回 403',
))
class ActivityFileView(APIView):
    permission_classes = (IsPresenterOrAdminOrReadOnly,)

    def post(self, request: WSGIRequest, id: int) -> Response:
        activity = get_object_or_404(Activity, id=id)
        self.check_object_permissions(request, activity)
        # if activity.folder


    def delete(self, request: WSGIRequest) -> Response:
        pass


class ActivityFileDone(APIView):
    pass