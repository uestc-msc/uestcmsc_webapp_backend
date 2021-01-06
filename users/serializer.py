from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from users.models import UserProfile
from utils import is_email, is_number


class UserRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(required=True,
                                     max_length=150,
                                     validators=[
                                         UniqueValidator(queryset=User.objects.all(), message="用户邮箱已存在")
                                     ])
    password = serializers.CharField(required=True,
                                     min_length=6,
                                     max_length=256)
    first_name = serializers.CharField(required=True,
                                       max_length=150)
    student_id = serializers.CharField(required=True,
                                       max_length=20,
                                       validators=[
                                           UniqueValidator(queryset=UserProfile.objects.all(), message="用户学号已存在")
                                       ])

    def validate_username(self, username):
        if not is_email(username):
            raise serializers.ValidationError("邮箱格式错误")
        if User.objects.filter(username=username).count() > 0:
            raise serializers.ValidationError("邮箱已存在")
        return username

    def validate_student_id(self, student_id):
        if not is_number(student_id):
            raise serializers.ValidationError("学号格式错误")
        if UserProfile.objects.filter(student_id=student_id).count() > 0:
            raise serializers.ValidationError("学号已存在")
        return student_id

    def create(self, validated_data):
        user = User.objects.create_user(username=validated_data["username"],
                                        password=validated_data["password"],
                                        first_name=validated_data["first_name"])
        user_profile = UserProfile.objects.create(user=user,
                                                  student_id=validated_data["student_id"])
        user.save()
        user_profile.save()
        return user


class UserListSerializer(serializers.Serializer):
    pass


class UserProfileSerializer(serializers.Serializer):
    pass