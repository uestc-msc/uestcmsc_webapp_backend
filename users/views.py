from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt
from .models import UserProfile
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from utils import *


# Create your views here.
@api_view(['POST'])
def signup(request):
    """
    用户注册，必需参数：
    username（非空，只包含数字字母 '_' '-'，数据库中不存在重复）
    password（不少于 6 位）
    first_name（非空）
    email（邮件格式，数据库中不存在重复）
    student_id（数字，数据库中不存在重复）

    参数错误或不符合以上任一要求，返回 400；否则成功注册并登陆，然后返回 200。
    """
    username, password, first_name, email, student_id = '', '', '', '', ''
    errmsg = ''
    data = request.data

    if 'username' not in data or len(data['username']) == 0:
        errmsg += "username should not be empty.\n"
    elif not is_valid_username(data['username']):
        errmsg += "username should only contain alphas, numbers and _-\n"
    elif User.objects.filter(username=data['username']).count() > 0:
        errmsg += "username already exists.\n"
    else:
        username = data['username']

    if 'password' not in data or len(data['password']) == 0:
        errmsg += "password should not be empty.\n"
    elif len(data['password']) < 6:
        errmsg += "password should be at least 6 letters.\n"
    else:
        password = data['password']

    if 'first_name' not in data or len(data['first_name']) == 0:
        errmsg += "first_name should not be empty.\n"
    else:
        first_name = data['first_name']

    if 'email' not in data or len(data['email']) == 0:
        errmsg += "email should not be empty.\n"
    elif not is_email(data['email']):
        errmsg += "email is not invalid.\n"
    elif User.objects.filter(email=data['email']).count() > 0:
        errmsg += "email already exists.\n"
    else:
        email = data["email"]

    if 'student_id' not in data or len(data['student_id']) == 0:
        errmsg += "student_id should not be empty.\n"
    elif not is_number(data['student_id']):
        errmsg += "student_id should be number.\n"
    elif UserProfile.objects.filter(student_id=data['student_id']).count() > 0:
        errmsg += "student_id already exists.\n"
    else:
        student_id = data['student_id']

    if errmsg == "": # 如果没有异常，则开始向数据库写入数据
        user = User.objects.create_user(username, email=email, password=password, first_name=first_name)
        up = UserProfile.objects.create(user=user, student_id=student_id)
        up.save()
        user = authenticate(request, username=username, password=password)
        django_login(request, user)
        return Response(status=status.HTTP_200_OK)
    else:
        return Response(data=errmsg, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):
    try:
        username_or_email = request.data['username']
        password = request.data['password']
        if is_email(username_or_email):
            username_or_email = User.objects.filter(email=username_or_email)[0].username
        user = authenticate(request, username=username_or_email, password=password)
        django_login(request, user)
        return Response(status=status.HTTP_200_OK)
    except IntegrityError or KeyError:
        return Response(data="username or password incorrect.", status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def forget_password(request):
    pass


@api_view(['POST'])
def reset_password(request):
    pass


@api_view(['GET'])
def logout(request):
    pass


@api_view(['GET', 'PUT'])
def profile(request, pk: int):
    pass