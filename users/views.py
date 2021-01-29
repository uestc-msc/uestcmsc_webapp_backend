from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters
from rest_framework.generics import *

from utils import MyPagination
from utils.permissions import *
from utils.swagger import *
from .serializer import UserSerializer


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_summary='获取用户列表',
    operation_description='获取用户列表（以及总页数），可对姓名、邮箱、学号进行搜索，并可指定页码和每页大小\n'
                          '数据作为 list 返回在 `results` 中，返回值的 `count` 为搜索结果的总数\n'
                          '返回结果以经验值降序排序\n'
                          '注：如页码不正确或不存在，返回 404\n'
                          '注：如每页大小不正确或不存在，使用默认每页大小（15）\n'
                          '注：如无搜索结果，返回 200，其中 `results` 为空',
    manual_parameters=[Param_search, Param_page, Param_page_size],
))
class UserListView(ListAPIView):
    queryset = User.objects.all().order_by("-userprofile__experience")
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username', 'first_name', 'last_name', 'userprofile__student_id')
    pagination_class = MyPagination
    serializer_class = UserSerializer


@method_decorator(name="get", decorator=swagger_auto_schema(
        operation_summary='获取用户信息',
        operation_description='获取一个的用户信息，成功返回 200\n'
                              # '注：需要登录，否则返回 403',
))
@method_decorator(name="put", decorator=swagger_auto_schema(
    operation_summary='更新用户信息',
    operation_description='响应报文和 PATCH 方法相同，但 PUT 要求在请求中提交所有信息',
    deprecated=True
))
@method_decorator(name="patch", decorator=swagger_auto_schema(
    operation_summary='更新用户部分信息',
    operation_description='更新一个用户的信息，成功返回 200\n'
                          '如用户不存在，返回 404\n'
                          '如更新的参数有错误，返回 400\n'
                          '注：需要是用户本人或管理员，否则返回 403\n'
                          '注：PATCH 方法可以只提交更新的值，也可以提交所有值'
))
class UserDetailView(RetrieveUpdateAPIView):
    permission_classes = (IsSelfOrAdminOrReadOnly, )
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'
