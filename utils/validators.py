import re
from typing import List

from django.contrib.auth.models import User
from rest_framework import serializers


# 判断字符串是否为邮箱
def is_email(string: str) -> bool:
    email_re = r'^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}$'
    return bool(re.match(email_re, string))


# 判断密码是否合法
def is_valid_password(string: str) -> bool:
    return len(string) >= 6


# 判断字符串是否为数字
def is_number(string: str) -> bool:
    try:
        int(string)
        return True
    except ValueError:
        return False


def validate_username(username):
    if not is_email(username):
        raise serializers.ValidationError("邮箱格式错误")
    if User.objects.filter(username=username):
        raise serializers.ValidationError("邮箱已存在")
    return username


def validate_student_id(student_id: str):
    if not is_number(student_id):
        raise serializers.ValidationError("学号格式错误")
    return student_id


# 检测用户存在
def validate_user_id(id: int):
    if not User.objects.filter(id=id):
        raise serializers.ValidationError("用户不存在")
    return id


# 检测名单中的用户均存在
def validate_user_ids(ids: List[int]):
    filters = User.objects.filter(id__in=ids)
    if len(filters) != len(ids):
        raise serializers.ValidationError("用户不存在")
    return ids
