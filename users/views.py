from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest
from django.http import Http404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, filters
from rest_framework.response import Response
from rest_framework.views import APIView

from utils import MyPagination
from utils.permissions import login_required, isOwnerOrAdmin
from utils.swagger import *
from .serializer import UserRegisterSerializer, UserSerializer


class UserListView(APIView):
    @swagger_auto_schema(
        operation_summary='获取用户信息的列表',
        operation_description='获取用户信息的列表（以及总页数），可对姓名、邮箱、学号进行搜索，并可指定页码和每页大小\n'
                              '注：需要登录',
        manual_parameters=[Param_keyword, Param_page, Param_page_size],
        responses={200: Schema_pagination(UserSerializer)},
    )
    @login_required
    def get(self, request: WSGIRequest) -> Response:
        pagination_class = MyPagination()
        search_class = filters.SearchFilter()
        self.search_fields = ['username', 'first_name', 'student_id']  # 需要搜索的字段
        user_lists = User.objects.all().order_by('-userprofile__experience')  # 用户列表
        queryset = search_class.filter_queryset(request, user_lists, self)  # 实例化搜索查询器
        page_query = pagination_class.paginate_queryset(queryset=queryset, request=request, view=self)  # 实例化分页器
        serializer = UserSerializer(page_query, many=True)  # 返回序列化
        page_result = pagination_class.get_paginated_response(serializer.data)  # 分页返回
        return page_result

    @swagger_auto_schema(
        operation_summary='注册新用户',
        operation_description='成功返回 201\n'
                              '失败（参数错误或不符合要求）返回 400',
        request_body=UserRegisterSerializer,
        responses={200: None}
    )
    def post(self, request: WSGIRequest) -> Response:
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    def get_object(self, pk: int) -> User:
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    @swagger_auto_schema(
        operation_summary='获取用户信息',
        operation_description='获取用户信息\n'
                              '注：需要登录',
        responses={200: UserSerializer},
    )
    @login_required
    def get(self, request: WSGIRequest, pk: int) -> Response:
        u = self.get_object(pk)
        serializer = UserSerializer(u)  # 此处还没有做鉴权
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary='更新用户信息',
        operation_description='更新用户信息，成功返回 201，如不存在，返回 404\n'
                              '注：PATCH 只要求需要更新的信息'
                              '注：需要是用户本人或管理员，否则返回 401（未登录）或 403（已登录的其他用户）',
        request_body=UserSerializer,
        responses={201: UserSerializer},
    )
    @login_required
    def patch(self, request: WSGIRequest, pk: int) -> Response:
        u = self.get_object(pk)
        if not isOwnerOrAdmin(request, u):
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = UserSerializer(u, data=request.data, partial=True)  # 此处也没有做鉴权
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"message":"参数错误"}, status=status.HTTP_400_BAD_REQUEST)
