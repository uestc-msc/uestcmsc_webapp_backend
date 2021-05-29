from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListAPIView

from activities_files.views import ActivityFileListView, ActivityFileDetailView
from activities_photos.serializer import ActivityPhotoSerializer
from utils import Pagination
from utils.permissions import *
from utils.swagger import *


# 连视图也复用 ActivityFileListView 了
from utils.validators import is_number


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_summary='获取沙龙图片列表',
    operation_description='获取沙龙图片列表（以及总长度），并可指定沙龙id、页码和每页大小\n'
                          '数据作为 list 返回在 `results` 中，返回值的 `count` 为搜索结果的总数\n'
                          '注：如页码不正确或不存在，返回 404\n'
                          '注：如每页大小不正确或不存在，使用默认每页大小（15）\n'
                          '注：如无搜索结果，返回 200，其中 `results` 为空\n',
    manual_parameters=[Param_activity, Param_page, Param_page_size],
))
@method_decorator(name='post', decorator=swagger_auto_schema(
    operation_summary='添加沙龙图片',
    operation_description='对 `activity_id` 对应沙龙添加图片\n'
                          '成功返回 201，沙龙或文件不存在返回 404\n'
                          '注：需要登录，否则返回 403\n'
                          '注 2：需先调用“创建文件上传会话”接口，上传完文件后才可以调用该接口\n'
                          '注 3：`file_id` 在向 Onedrive 上传完成的响应中\n'
                          '注 4：如果文件重名，会自动重命名；最终文件名以响应报文为准',
    request_body=Schema_object(Schema_activity_id, Schema_file_id),
    responses={201: ActivityPhotoSerializer()}
))
class ActivityPhotoListView(ActivityFileListView, ListAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ActivityPhotoSerializer
    pagination_class = Pagination

    def get_queryset(self):
        # 按创建日期降序排序
        queryset = self.model_class.objects.all().order_by('-created_datetime')
        activity_id = self.request.query_params.get('activity', None)
        if activity_id:
            if not is_number(activity_id):
                raise Http404
            queryset = queryset.filter(activity_id=activity_id)
        return queryset


# 连视图也复用 ActivityFileDetailView 了
@method_decorator(name='delete', decorator=swagger_auto_schema(
    operation_summary='删除沙龙图片',
    operation_description='删除 `file_id` 对应的沙龙图片\n'
                          '成功返回 204，沙龙或图片不存在返回 404\n'
                          '注：需要是上传者/沙龙主讲人/管理员，否则返回 403'
))
class ActivityPhotoDetailView(ActivityFileDetailView):
    serializer_class = ActivityPhotoSerializer
