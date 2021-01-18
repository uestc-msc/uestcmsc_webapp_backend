from datetime import datetime, timedelta

from django.core.handlers.wsgi import WSGIRequest
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

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
        operation_description='成功返回 201'
                              '失败（参数错误或不符合要求）返回 400',
        request_body=UserRegisterSerializer,
        responses={200:None}
    )
    def post(self, request: WSGIRequest) -> Response:
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
def profile(request: WSGIRequest, pk: int) -> Response:
    pass
