from datetime import timedelta

from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest
from django.utils.timezone import now
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from accounts.serializer import UserRegisterSerializer
from users.models import ResetPasswordRequest
from users.serializer import UserSerializer
from utils import generate_uuid, is_valid_password
from utils.mail import send_reset_password_email
from utils.permissions import login_required
from utils.swagger import *


@swagger_auto_schema(
    method='POST',
    operation_summary='注册新用户',
    operation_description='成功返回 201\n'
                          '失败（参数错误或不符合要求）返回 400',
    request_body=UserRegisterSerializer,
    responses={201: UserSerializer()}
)
@api_view(['POST'])
def signup(request: WSGIRequest) -> Response:
    register_serializer = UserRegisterSerializer(data=request.data)
    if register_serializer.is_valid():
        u = register_serializer.save()
        user_serializer = UserSerializer(u)
        return Response(user_serializer.data, status=status.HTTP_201_CREATED)
    return Response(register_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='POST',
    operation_summary='登录',
    operation_description='成功返回 200'
                          '失败（账户或密码错误）返回 401\n'
                          '注：一个已登录的用户 A 尝试 login 账户 B 失败后，仍具有账户 A 的凭证。',
    request_body=Schema_object(Schema_email, Schema_password),
    responses={200: Schema_none}
)
@api_view(['POST'])
def login(request: WSGIRequest) -> Response:
    err_response = Response(status=status.HTTP_401_UNAUTHORIZED)
    if 'username' not in request.data or 'password' not in request.data:
        return err_response
    username = request.data['username']
    password = request.data['password']
    user = authenticate(request, username=username, password=password)
    if user is None:
        return err_response
    django_login(request, user)
    return Response(status=status.HTTP_200_OK)  # 尽量改为 /user/<id>的东西


@swagger_auto_schema(
    method='POST',
    operation_summary='登出',
    operation_description='成功返回 204，失败（未登陆用户请求登出）返回 401。',
    responses={200: Schema_none}
)
@api_view(['POST'])
@login_required
def logout(request: WSGIRequest) -> Response:
    django_logout(request)
    return Response(status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(
    method='POST',
    operation_summary='忘记密码',
    operation_description='服务器生成 token 并发送至用户邮箱，然后返回 202\n'
                          '若用户邮件不存在，服务器拒绝服务并返回 400 `{"detail": "邮箱参数不存在或不正确"}`\n'
                          '若用户操作过于频繁（同 IP 1 分钟内只能发送 1 封，24 小时内只能发送 10 封），服务器拒绝服务并返回 403 `{"detail": "发送邮件过于频繁"}`\n'
                          '邮件发送失败，返回 500 `{"detail": "发送邮件失败"}`\n'
                          '注：token 24 小时有效，新 token 不会使旧 token 失效',
    request_body=Schema_object(Schema_email),
    responses={200: Schema_none}
)
@api_view(['POST'])
def forget_password(request: WSGIRequest) -> Response:
    # 获取时间
    current = now()
    one_min_ago = current - timedelta(minutes=1)
    one_day_ago = current - timedelta(days=1)
    ResetPasswordRequest.objects.filter(request_time__lt=one_day_ago).delete()  # 删除一天前的所有请求
    # 判断邮箱是否存在
    if 'email' not in request.POST or User.objects.filter(username=request.POST['email']).count() == 0:
        return Response({"detail": "邮箱参数不存在或不正确"}, status=status.HTTP_400_BAD_REQUEST)
    email = request.POST['email']
    user = User.objects.filter(username=email).first()
    # 获取 ip
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ipv4addr = x_forwarded_for.split(',')[0]
    else:
        ipv4addr = request.META.get('REMOTE_ADDR')
    # 判断是否发送频繁
    if ResetPasswordRequest.objects \
            .filter(ipv4addr=ipv4addr, request_time__gte=one_min_ago) \
            .count() >= 1 or \
            ResetPasswordRequest.objects \
                    .filter(ipv4addr=ipv4addr, request_time__gte=one_day_ago) \
                    .count() >= 10:
        return Response({"detail": "发送邮件过于频繁"}, status=status.HTTP_403_FORBIDDEN)
    # 生成 token
    token = generate_uuid()
    # 发送邮件并存储记录
    if send_reset_password_email(email, user.first_name, token, current):
        reset_password_request = ResetPasswordRequest(user=user, ipv4addr=ipv4addr, token=token,
                                                      request_time=current)
        reset_password_request.save()
        return Response(status=status.HTTP_202_ACCEPTED)
    else:
        return Response({"detail": "发送邮件失败"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='POST',
    operation_summary='验证邮箱重置密码',
    operation_description='若没有 token 参数，返回 400 `{"detail": "缺少 token 参数"}`\n'
                          '若参数 token 无效或已过期（24 小时），返回 403 `{"detail": "token 无效"}`\n'
                          '若参数 token 有效，且没有 new_password 参数，返回 200 `{"detail": "token 有效"}`\n'
                          '若参数 token 有效，且参数 new_password 不合法，返回 400 `{"detail": "新密码不合法"}`\n'
                          '若参数 token 有效，且参数 new_password 合法，修改密码、使用户下线并返回 204\n',
    request_body=Schema_object(Schema_token, Schema_new_password),
)
@api_view(['POST'])
def reset_password(request: WSGIRequest) -> Response:
    current = now()
    if "token" not in request.POST:
        return Response({"detail": "缺少 token 参数"}, status=status.HTTP_400_BAD_REQUEST)
    token = request.POST["token"]
    request_record = ResetPasswordRequest.objects.filter(token=token).first()
    if request_record is None or request_record.request_time + timedelta(days=1) < current:  # 若不存在，或在一天以前发出的
        return Response({"detail": "token 无效"}, status=status.HTTP_403_FORBIDDEN)
    if "new_password" not in request.POST:
        return Response({"detail": "token 有效"}, status=status.HTTP_200_OK)
    new_password = request.POST["new_password"]
    if not is_valid_password(new_password):
        return Response({"detail": "新密码不合法"}, status=status.HTTP_400_BAD_REQUEST)
    request_record.user.set_password(new_password)
    request_record.user.save()
    request_record.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(
    method='POST',
    operation_summary='修改密码',
    operation_description='若用户未登录，返回 401\n'
                          '若登录用户和 `{id}` 不同，返回 403\n'
                          '若参数 old_password 和 new_password 不都存在，返回 400 `{"detail": "缺少参数 old_response 或 new_password"}`\n'
                          '若 old_password 和原密码不同，返回 401 `{"detail": "原密码不匹配"}`\n'
                          '若 new_password 不合法，返回 400 `{"detail": "新密码不合法"}`\n'
                          '若 old_password 和 new_password 均正确，修改密码、使用户下线并返回 204\n',
    request_body=Schema_object(Schema_old_password, Schema_new_password),
    responses={200: Schema_none}
)
@api_view(['POST'])
@login_required
def change_password(request: WSGIRequest) -> Response:
    if "old_password" not in request.POST or "new_password" not in request.POST:
        return Response({"detail": "缺少参数 old_response 或 new_password"}, status=status.HTTP_400_BAD_REQUEST)
    old_password = request.POST["old_password"]
    new_password = request.POST["new_password"]
    if not authenticate(request, username=request.user.username, password=old_password):
        return Response({"detail": "原密码不匹配"}, status=status.HTTP_401_UNAUTHORIZED)
    if not is_valid_password(new_password):
        return Response({"detail": "新密码不合法"}, status=status.HTTP_400_BAD_REQUEST)
    request.user.set_password(new_password)
    request.user.save()
    return Response(status=status.HTTP_204_NO_CONTENT)
