from datetime import timedelta

from django.contrib.auth import authenticate, login as django_login, logout as django_logout

from django.middleware import csrf
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from accounts.serializer import UserRegisterSerializer
from users.models import User, ResetPasswordRequest
from users.serializer import UserSerializer
from utils.mail import send_reset_password_email
from utils.permissions import login_required
from utils.random import generate_uuid
from utils.swagger import *
from utils.validators import is_valid_password


@swagger_auto_schema(
    method='POST',
    operation_summary='注册新用户',
    operation_description='成功注册新账户：返回 201\n'
                          '成功绑定微信小程序账户：返回200\n'
                          '失败（参数错误或不符合要求）：返回 400\n'
                          '注：注册以后不会自动登录',
    request_body=UserRegisterSerializer,
    responses={201: UserSerializer()}
)
@api_view(['POST'])
@csrf_exempt
def signup(request: Request) -> Response:
    register_serializer = UserRegisterSerializer(data=request.data)
    if not register_serializer.is_valid():
        return Response(register_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(userprofile__student_id=register_serializer.validated_data['student_id']):
        # 判断注册的用户是微信小程序用户：姓名和学号与数据库中相同，且数据库中密码为空
        # 如果满足条件，则将找到的用户的信息更新，然后返回 200
        origin_wechat_user = User.objects.filter(
            userprofile__student_id=register_serializer.validated_data['student_id'],
            first_name=register_serializer.validated_data['first_name'],
            password='')
        if origin_wechat_user:
            u = origin_wechat_user[0]
            user_serializer = UserSerializer(u)
            user_serializer.update(u, register_serializer.validated_data)
            return Response(user_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(data={"student_id": "学号已存在"}, status=status.HTTP_400_BAD_REQUEST)
    u = register_serializer.save()
    user_serializer = UserSerializer(u)
    return Response(user_serializer.data, status=status.HTTP_201_CREATED)


@swagger_auto_schema(
    method='POST',
    operation_summary='登录',
    operation_description='成功返回 200\n'
                          '失败（账户或密码错误）返回 401\n'
                          '注 1：成功返回的字段中还包含了 csrftoken，请将其按照[文档](https://docs.djangoproject.com/zh-hans/3.1/ref/csrf/)所示方法加入 cookie 和 header'
                          '注 2：一个已登录的用户 A 尝试 login 账户 B 失败后，仍具有账户 A 的凭证。',
    request_body=Schema_object(Schema_email, Schema_password),
    responses={200: UserSerializer()}
)
@api_view(['POST'])
@csrf_exempt
def login(request: Request) -> Response:
    err_response = Response(status=status.HTTP_401_UNAUTHORIZED)
    if 'username' not in request.data or 'password' not in request.data:
        return err_response
    username = request.data['username']
    password = request.data['password']
    user = authenticate(request, username=username, password=password)
    if user is None:
        return err_response
    django_login(request, user)
    serializer_data = UserSerializer(user).data
    serializer_data['csrftoken'] = csrf.get_token(request)
    return Response(serializer_data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='POST',
    operation_summary='登出',
    operation_description='成功返回 204，失败（未登陆用户请求登出）返回 401。',
    responses={200: Schema_None}
)
@api_view(['POST'])
@login_required
@csrf_exempt
def logout(request: Request) -> Response:
    django_logout(request)
    return Response(status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(
    method='POST',
    operation_summary='忘记密码',
    operation_description='服务器生成 token 并发送至用户邮箱，成功返回 202（已请求发送邮件，但不代表发送成功）\n'
                          '若用户邮件不存在，服务器拒绝服务并返回 400 `{"detail": "邮箱参数不存在或不正确"}`\n'
                          '若用户操作过于频繁（同 IP 1 分钟内只能发送 1 封，24 小时内只能发送 10 封），服务器拒绝服务并返回 403 `{"detail": "发送邮件过于频繁"}`\n'
                          '邮件发送失败，返回 500 `{"detail": "发送邮件失败"}`\n'
                          '注：token 24 小时有效，新 token 不会使旧 token 失效',
    request_body=Schema_object(Schema_email),
    responses={200: Schema_None}
)
@api_view(['POST'])
@csrf_exempt
def forget_password(request: Request) -> Response:
    # 获取时间
    current = now()
    one_min_ago = current - timedelta(minutes=1)
    one_day_ago = current - timedelta(days=1)
    ResetPasswordRequest.objects.filter(request_time__lt=one_day_ago).delete()  # 删除一天前的所有请求
    # 判断邮箱是否存在
    if 'email' not in request.data or User.objects.filter(username=request.data['email']).count() == 0:
        return Response({"detail": "用户不存在"}, status=status.HTTP_400_BAD_REQUEST)
    email = request.data['email']
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
    send_reset_password_email(email, user.first_name, token)
    reset_password_request = ResetPasswordRequest(user=user, ipv4addr=ipv4addr, token=token, request_time=current)
    reset_password_request.save()
    return Response({"detail": "我们已向您的邮箱发送了邮件，请留意收件箱和垃圾邮件"}, status=status.HTTP_202_ACCEPTED)


@swagger_auto_schema(
    method='POST',
    operation_summary='验证邮箱重置密码',
    operation_description='若没有 token 参数，返回 400 `{"detail": "缺少 token 参数"}`\n'
                          '若参数 token 无效或已过期（24 小时），返回 403 `{"detail": "token 错误或已过期"}`\n'
                          '若参数 token 有效，且没有 new_password 参数，返回 200 `{"detail": "token 有效"}`\n'
                          '若参数 token 有效，且参数 new_password 不合法，返回 400 `{"detail": "新密码不合法"}`\n'
                          '若参数 token 有效，且参数 new_password 合法，修改密码、使用户下线并返回 204\n',
    request_body=Schema_object(Schema_token, Schema_new_password),
)
@api_view(['POST'])
@csrf_exempt
def reset_password(request: Request) -> Response:
    current = now()
    if "token" not in request.data:
        return Response({"detail": "缺少 token 参数"}, status=status.HTTP_400_BAD_REQUEST)
    token = request.data["token"]
    request_record = ResetPasswordRequest.objects.filter(token=token).first()
    if request_record is None or request_record.request_time + timedelta(days=1) < current:  # 若不存在，或在一天以前发出的
        return Response({"detail": "token 错误或已过期"}, status=status.HTTP_403_FORBIDDEN)
    if "new_password" not in request.data:
        return Response({"detail": "token 有效"}, status=status.HTTP_200_OK)
    new_password = request.data["new_password"]
    if not is_valid_password(new_password):
        return Response({"detail": "新密码不合法"}, status=status.HTTP_400_BAD_REQUEST)
    request_record.user.set_password(new_password)
    request_record.user.save()
    request_record.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
