from django.contrib.auth.models import User
from rest_framework import serializers

from users.models import UserProfile
from utils.validators import validate_username, validate_student_id


class UserRegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(required=True, min_length=6, max_length=256)
    first_name = serializers.CharField(required=True)
    student_id = serializers.CharField(required=True, max_length=20)

    def validate_username(self, username):
        return validate_username(username)

    def validate_student_id(self, student_id):
        return validate_student_id(student_id)

    def create(self, validated_data):
        student_id = validated_data.pop('student_id')
        user = User.objects.create_user(**validated_data)
        user_profile = UserProfile.objects.create(user=user, student_id=student_id)
        user.save()
        user_profile.save()
        return user
