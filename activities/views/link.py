from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import *

from activities.models import ActivityLink
from activities.serializer import LinkSerializer
from utils.permissions import *
from utils.swagger import *


@method_decorator(name='post', decorator=swagger_auto_schema(
    operation_summary='添加沙龙相关链接',
    operation_description='对 `activity_id` 对应沙龙添加链接\n'
                          '成功返回 201，沙龙不存在返回 404\n'
                          '注：需要是沙龙演讲者或管理员，否则返回 403',
    request_body=Schema_object(Schema_activity_id, Schema_url)
))
class ActivityLinkCreateView(GenericAPIView):
    permission_classes = (IsPresenterOrAdminOrReadOnly,)
    serializer_class = LinkSerializer

    def post(self, request: WSGIRequest) -> Response:
        activity_id = request.data.get('activity_id', None)
        url = request.data.get('url', None)
        if not activity_id or not url:
            return Response({"detail": "activity_id 或 url 参数不存在"}, status=status.HTTP_400_BAD_REQUEST)
        link = ActivityLink.objects.create(activity_id=activity_id, url=url)
        serializer = LinkSerializer(link)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@method_decorator(name="get", decorator=swagger_auto_schema(
    operation_summary='获取沙龙相关链接'
))
@method_decorator(name="put", decorator=swagger_auto_schema(
    operation_summary='更新沙龙相关链接',
    operation_description='用于更新对应链接，成功返回 200\n'
                          '注：需要是沙龙演讲者或管理员，否则返回 403',
))
@method_decorator(name="patch", decorator=swagger_auto_schema(
    operation_summary='更新沙龙相关链接（部分）',
    operation_description='同 PUT',
))
@method_decorator(name="delete", decorator=swagger_auto_schema(
    operation_summary='删除沙龙相关链接',
    operation_description='删除 `id` 对应的沙龙相关链接，成功返回 204\n'
                          '注：需要是沙龙演讲者或管理员，否则返回 403'
))
class ActivityLinkDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsPresenterOrAdminOrReadOnly,)
    queryset = ActivityLink.objects.all()
    serializer_class = LinkSerializer
    lookup_field = 'id'

