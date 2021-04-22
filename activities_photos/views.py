from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema

from activities.serializer import ActivityFileSerializer
from activities_files.views import ActivityFileListView, ActivityFileDetailView
from activities_photos.models import ActivityPhoto
from activities_photos.serializer import ActivityPhotoSerializer
from utils.permissions import *
from utils.swagger import *


# 连视图也复用 ActivityFileListView 了
@method_decorator(name='post', decorator=swagger_auto_schema(
    operation_summary='添加沙龙图片',
    operation_description='对 `activity_id` 对应沙龙添加图片\n'
                          '成功返回 201，沙龙或文件不存在返回 404\n'
                          '注：需要登录，否则返回 403'
                          '注 2：需先调用“创建文件上传会话”接口，上传完文件后才可以调用该接口'
                          '注 3：`file_id` 在向 Onedrive 上传完成的响应中',
    request_body=Schema_object(Schema_activity_id, Schema_file_id),
    responses={201: ActivityPhotoSerializer()}
))
class ActivityPhotoListView(ActivityFileListView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ActivityPhotoSerializer


# 连视图也复用 ActivityFileDetailView 了
@method_decorator(name='delete', decorator=swagger_auto_schema(
    operation_summary='删除沙龙图片',
    operation_description='删除 `file_id` 对应的沙龙图片\n'
                          '成功返回 204，沙龙或图片不存在返回 404\n'
                          '注：需要是上传者/沙龙主讲人/管理员，否则返回 403'
))
class ActivityPhotoDetailView(ActivityFileDetailView):
    serializer_class = ActivityPhotoSerializer
