from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters
from rest_framework.decorators import api_view
from rest_framework.generics import *
from rest_framework.permissions import *

from activities.models import Activity
from activities.serializer import ActivitySerializer
from utils import MyPagination
from utils.permissions import *
from utils.swagger import *


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_summary='获取沙龙列表',
    operation_description='获取沙龙列表（以及总页数），可对标题和演讲者姓名进行搜索，并可指定页码和每页大小\n'
                          '数据作为 list 返回在 `results` 中，返回值的 `count` 为搜索结果的总数'
                          '注：如页码不正确或不存在，返回 404 `{"detail": "无效页面。"}`\n'
                          '注：如无搜索结果，返回 200，其中 `results` 为空',
    manual_parameters=[Param_search, Param_page, Param_page_size],
))
@method_decorator(name='post', decorator=swagger_auto_schema(
    operation_summary='创建沙龙',
    operation_description='成功返回 201，参数错误返回 400',
))
class ActivityListView(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Activity.objects.all().order_by("-datetime")
    filter_backends = (filters.SearchFilter,)
    search_fields = ('title', 'presenter__first_name')
    pagination_class = MyPagination
    serializer_class = ActivitySerializer


@method_decorator(name="get", decorator=swagger_auto_schema(
        operation_summary='获取沙龙信息',
        operation_description='获取沙龙信息\n'
                              '注：需要登录',
))
@method_decorator(name="put", decorator=swagger_auto_schema(
    operation_summary='更新沙龙信息',
    operation_description='更新沙龙信息，成功返回 201\n'
                          '如不存在，返回 404\n'
                          '如更新的参数有错误，返回 400 `{"detail":"参数错误"}`\n'
                          '注：需要是沙龙演讲者或管理员，否则返回 401（未登录）或 403（已登录的其他用户）',
))
@method_decorator(name="patch", decorator=swagger_auto_schema(
    operation_summary='更新沙龙部分信息',
    operation_description='更新沙龙部分信息，成功返回 201\n'
                          '如不存在，返回 404\n'
                          '如更新的参数有错误，返回 400 `{"detail":"参数错误"}`\n'
                          '注：需要是沙龙演讲者或管理员，否则返回 401（未登录）或 403（已登录的其他用户）',
))
class ActivityDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, IsPresenterOrAdminOrReadOnly, )
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer


@api_view(['POST'])
def activity_check_in(request: WSGIRequest) -> Response:
    return None