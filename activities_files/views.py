import os

from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import *
from rest_framework.views import APIView

from activities.serializer import ActivityFileSerializer
from activities_files.models import ActivityFile
from cloud.models import OnedriveFile
from cloud.onedrive import onedrive_drive, OnedriveUnavailableException
from cloud.onedrive.activities import get_or_create_activity_folder
from cloud.onedrive.api.request import log_onedrive_error
from utils.permissions import *
from utils.swagger import *


# 该类被 ActivityPhotoListView 复用
@method_decorator(name='post', decorator=swagger_auto_schema(
    operation_summary='添加沙龙文件',
    operation_description='对 `activity_id` 对应沙龙添加文件\n'
                          '成功返回 201，沙龙或文件不存在返回 404\n'
                          '注：需要是沙龙演讲者或管理员，否则返回 403\n'
                          '注 2：需先调用“创建文件上传会话”接口，上传完文件后才可以调用该接口\n'
                          '注 3：`key` 在向 Onedrive 上传完成的响应中\n'
                          '注 4：如果文件重名，会自动重命名；最终文件名以响应报文为准',
    request_body=Schema_object(Schema_activity_id, Schema_file_id),
    responses={201:ActivityFileSerializer()}
))
class ActivityFileListView(GenericAPIView):
    permission_classes = (IsPresenterOrAdminOrReadOnly,)
    serializer_class = ActivityFileSerializer

    @property
    def model_class(self):
        return self.serializer_class.Meta.model

    def post(self, request: Request) -> Response:
        activity_id = request.data.get('activity_id', None)
        file_id = request.data.get('key', None)
        if not activity_id or not file_id:
            return Response({"detail": "activity_id 或 key 参数不存在"}, status=status.HTTP_400_BAD_REQUEST)
        # 获取活动文件夹
        folder = get_or_create_activity_folder(activity_id)
        # 将文件移动至活动文件夹（并验证有效性）
        # 这里懒得考虑活动文件夹在 Onedrive 被删的异常情况
        # 考虑重名的问题：由于本地没有文件信息，假设重名是小概率事件，所以先尝试文件移动，如果冲突再获取文件信息、进一步处理
        response = onedrive_drive.find_file_by_id(file_id).move(folder.id, fail_silently=True)
        if response.status_code == status.HTTP_409_CONFLICT:
            # 如果发生重名，直接从 Onedrive 获取完整名单，然后对着名单改名
            fullname = onedrive_drive.find_file_by_id(file_id).get_metadata().json()['name']
            filename, file_extension = os.path.splitext(fullname)
            response = onedrive_drive.find_file_by_id(folder.id).list_children()
            exist_filenames = list(map(lambda f: f['name'], response.json()['value']))
            i = 1
            # 重命名格式: oldname(1).jpg
            while fullname in exist_filenames:
                fullname = f'{filename} ({i}){file_extension}'
                i += 1
            response = onedrive_drive.find_file_by_id(file_id).move(folder.id, fullname)
        elif not response.ok:
            log_onedrive_error(response)
            raise OnedriveUnavailableException
        # 创建数据库记录，并获取其他信息
        file = self.model_class.create_file(file_info=response.json(), uploader=request.user, activity_id=activity_id)
        serializer = self.serializer_class(file)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@method_decorator(name='delete', decorator=swagger_auto_schema(
    operation_summary='删除沙龙文件',
    operation_description='删除 `key` 对应的沙龙文件\n'
                          '成功返回 204，沙龙或文件不存在返回 404\n'
                          '注：需要是沙龙演讲者或管理员，否则返回 403'
))
class ActivityFileDetailView(DestroyAPIView):
    permission_classes = (IsUploaderOrPresenterOrAdminOrReadOnly,)
    serializer_class = ActivityFileSerializer
    lookup_field = 'id'

    @property
    def model_class(self):
        return self.serializer_class.Meta.model

    @property
    def queryset(self):
        return self.serializer_class.Meta.model.objects.all()

    def perform_destroy(self, instance: OnedriveFile):
        response = instance.driveitem.delete(fail_silently=True)
        if response.ok or response.status_code == status.HTTP_404_NOT_FOUND:
            instance.delete()
        else:
            log_onedrive_error(response)
            raise OnedriveUnavailableException
