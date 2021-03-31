from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import *

from activities.serializer import ActivityFileSerializer
from utils.onedrive.activities import get_or_create_activity_folder
from utils.permissions import *
from utils.swagger import *


@method_decorator(name='post', decorator=swagger_auto_schema(
    operation_summary='添加沙龙相关文件',
    operation_description='对 `activity_id` 对应沙龙添加文件\n'
                          '成功返回 201，沙龙或文件不存在返回 404\n'
                          '注：需要是沙龙演讲者或管理员，否则返回 403'
                          '注 2：需先调用“创建文件上传会话”接口，上传完文件后才可以调用该接口'
                          '注 3：`file_id` 在向 Onedrive 上传完成的响应中',
    request_body=Schema_object(Schema_activity_id, Schema_file_id)
))
class ActivityFileListView(GenericAPIView):
    permission_classes = (IsPresenterOrAdminOrReadOnly,)
    serializer_class = ActivityFileSerializer

    def post(self, request: Request) -> Response:
        activity_id = request.data.get('activity_id', None)
        file_id = request.data.get('file_id', None)
        if not activity_id or not file_id:
            return Response({"detail": "activity_id 或 file_id 参数不存在"}, status=status.HTTP_400_BAD_REQUEST)

        folder = get_or_create_activity_folder(activity_id)
        pass


        # return Response(serializer.data, status=status.HTTP_201_CREATED)


class ActivityFileDetailView(GenericAPIView):
    pass
