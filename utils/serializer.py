from django.contrib.auth.models import User
from rest_framework import serializers

from users.models import UserProfile
from utils import is_email, is_number


def validate_username(username):
    if not is_email(username):
        raise serializers.ValidationError("邮箱格式错误")
    if User.objects.filter(username=username):
        raise serializers.ValidationError("邮箱已存在")
    return username


def validate_student_id(student_id):
    if not is_number(student_id):
        raise serializers.ValidationError("学号格式错误")
    if UserProfile.objects.filter(student_id=student_id):
        raise serializers.ValidationError("学号已存在")
    return student_id


def validate_user_list(user_list):
    for user in user_list:
        if not User.objects.filter(id=user['id']):
            raise serializers.ValidationError("用户不存在")


def validate_userid_list(id_list):
    for id in id_list:
        if not User.objects.filter(id=id):
            raise serializers.ValidationError("用户不存在")