from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.views.decorators.csrf import csrf_exempt
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, mixins, generics

from utils import is_email
from .serializer import UserRegisterSerializer, UserListSerializer


class UserView(APIView):
    # @swagger_auto_schema(
    #     operation_summary='获取用户列表',
    #     operation_description='获取用户列表，成功返回 200，失败返回 400\n',
    #     request_body=UserListSerializer,
    # )
    def get(self):
        pass

    @swagger_auto_schema(
        operation_summary='注册新用户',
        operation_description='注册新用户，成功返回 201，失败返回 400',
        request_body=UserRegisterSerializer
    )
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='POST',
    operation_summary='登录',
    operation_description='成功返回 200，失败返回 401。\n注意一个已登录的用户尝试 login 另外一个账户失败后，仍具有第一个账户的凭证。',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT, properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING, description='邮箱'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='密码'),
        }
    ),
)
@api_view(['POST'])
def login(request):
    err_response = Response(status=status.HTTP_401_UNAUTHORIZED)
    if 'username' not in request.data or 'password' not in request.data:
        return err_response
    username = request.data['username']
    password = request.data['password']
    user = authenticate(request, username=username, password=password)
    if user is None:
        return err_response
    django_login(request, user)
    return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
def forget_password(request):
    pass


@api_view(['POST'])
def reset_password(request):
    pass

@swagger_auto_schema(
    method='GET',
    operation_summary='注销',
    operation_description='成功返回 204，失败（未登陆用户请求注销）返回 401。'
)
@api_view(['GET'])
def logout(request):
    if request.user.is_authenticated:
        django_logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET', 'PUT'])
def profile(request, pk: int):
    pass