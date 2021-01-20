from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters
from rest_framework.generics import *

from utils import MyPagination
from utils.permissions import *
from utils.swagger import *
from .serializer import UserRegisterSerializer, UserSerializer


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_summary='获取用户列表',
    operation_description='获取用户列表（以及总页数），可对姓名、邮箱、学号进行搜索，并可指定页码和每页大小\n'
                          '数据作为 list 返回在 `results` 中，返回值的 `count` 为搜索结果的总数'
                          '注：如页码不正确或不存在，返回 404 `{"detail": "无效页面。"}`\n'
                          '注：如无搜索结果，返回 200，其中 `results` 为空',
    manual_parameters=[Param_search, Param_page, Param_page_size],
))
class UserListView(ListCreateAPIView):
    permission_classes = (IsAuthenticatedOrPostOnly,)
    queryset = User.objects.all().order_by("-userprofile__experience")
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username', 'first_name', 'last_name', 'userprofile__student_id')
    pagination_class = MyPagination
    serializer_class = UserSerializer

    @swagger_auto_schema(
        operation_summary='注册新用户',
        operation_description='成功返回 201\n'
                              '失败（参数错误或不符合要求）返回 400',
        request_body=UserRegisterSerializer,
    )
    def post(self, request) -> Response:
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(name="get", decorator=swagger_auto_schema(
        operation_summary='获取用户信息',
        operation_description='获取用户信息\n'
                              '注：需要登录',
))
@method_decorator(name="put", decorator=swagger_auto_schema(
    operation_summary='更新用户信息',
    operation_description='更新用户信息，成功返回 201\n'
                          '如不存在，返回 404\n'
                          '如更新的参数有错误，返回 400 `{"detail":"参数错误"}`\n'
                          '注：需要是用户本人或管理员，否则返回 401（未登录）或 403（已登录的其他用户）',
))
@method_decorator(name="patch", decorator=swagger_auto_schema(
    operation_summary='更新用户部分信息',
    operation_description='更新用户部分信息，成功返回 201\n'
                          '如不存在，返回 404\n'
                          '如更新的参数有错误，返回 400 `{"detail":"参数错误"}`\n'
                          '注：需要是用户本人或管理员，否则返回 401（未登录）或 403（已登录的其他用户）',
))
class UserDetailView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated, IsSelfOrAdminOrReadOnly, )
    queryset = User.objects.all()
    serializer_class = UserSerializer
