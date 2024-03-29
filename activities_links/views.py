from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import *

from utils.permissions import *
from utils.swagger import *
from .models import ActivityLink
from .serializer import LinkSerializer


@method_decorator(name='post', decorator=swagger_auto_schema(
    operation_summary='添加沙龙相关链接',
    operation_description='对 `activity_id` 对应沙龙添加链接\n'
                          '成功返回 201，沙龙不存在返回 404\n'
                          '注 1：需要是沙龙演讲者或管理员，否则返回 403'
                          '注 2：如果该沙龙已经有相同的链接，返回 409',
    request_body=Schema_object(Schema_activity_id, Schema_url)
))
class ActivityLinkListView(GenericAPIView):
    permission_classes = (IsPresenterOrAdminOrReadOnly,)
    serializer_class = LinkSerializer
    # TODO: 重名链接的 post put patch test，测试注意其他活动的相同链接的情况

    def post(self, request: Request) -> Response:
        activity_id = request.data.get('activity_id', None)
        if not activity_id:                                                 # 检查 activity_id 参数是否存在
            return Response({"detail": "activity_id 参数不存在"}, status=status.HTTP_400_BAD_REQUEST)
        activity = get_object_or_404(Activity, id=activity_id)              # 检查沙龙是否存在
        self.check_object_permissions(request, activity)                    # 检查权限
        url = request.data.get('url', '')
        if url == '':                                                       # 检查 url 是否为空
            return Response({"detail": "url 不能为空"}, status=status.HTTP_400_BAD_REQUEST)
        if ActivityLink.objects.filter(activity=activity, url=url):         # 检查该沙龙是否有重复链接
            return Response({"detail": "url 已存在"}, status=status.HTTP_409_CONFLICT)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)                           # 检查其他参数是否合法

        link = ActivityLink.objects.create(activity=activity, **serializer.data)
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
    permission_classes = (IsActivityPresenterOrAdminOrReadOnly,)
    queryset = ActivityLink.objects.all()
    serializer_class = LinkSerializer
    lookup_field = 'id'

    def update(self, request, *args, **kwargs) -> Response:
        link = self.get_object()
        url = request.data.get('url', '')
        if url == '':                                                       # 检查 url 是否为空
            return Response({"detail": "url 不能为空"}, status=status.HTTP_400_BAD_REQUEST)
        if ActivityLink.objects.filter(activity=link.activity, url=url):    # 检查该沙龙是否有重复链接
            return Response({"detail": "url 已存在"}, status=status.HTTP_409_CONFLICT)
        link.url = url
        link.save()
        serializer = LinkSerializer(link)
        return Response(serializer.data, status=status.HTTP_200_OK)
