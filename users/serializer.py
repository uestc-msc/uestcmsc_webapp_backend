from django.contrib.auth.models import User
from rest_framework import serializers

from users.models import UserProfile
from utils.validators import validate_student_id, validate_user_id


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id", "username", "first_name", "last_name",
            "student_id", "experience", "about", "subscribe_email", "avatar_url",
            "last_login", "date_joined", "is_staff", "is_superuser")
        read_only_fields = ('id', 'username',
                            'experience', 'avatar_url',
                            'last_login', 'date_joined', 'is_staff', 'is_superuser')

    # user 中需要单独设置的字段
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150, allow_blank=True)
    # userprofile 中的可读写字段
    student_id = serializers.CharField(source='userprofile.student_id', max_length=20)
    about = serializers.CharField(source='userprofile.about', allow_blank=True)
    subscribe_email = serializers.BooleanField(source='userprofile.subscribe_email')
    # userprofile 中的只读字段
    experience = serializers.ReadOnlyField(source='userprofile.experience')
    avatar_url = serializers.ReadOnlyField(source='userprofile.get_avatar')

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        # 隐藏 username 和 student_id
        request = self.context.get('request')
        if request is None:     # django shell 时会出现 request is None
            return ret
        if not (request.user.is_staff or request.user.is_superuser or request.user.id == ret['id']):
            ret['username'] = '***'
            ret['student_id'] = ret['student_id'][0:4]
        return ret

    def validate_student_id(self, student_id):
        return validate_student_id(student_id)

    def update(self, instance: User, validated_data):
        userprofile_data = validated_data.pop('userprofile', {})  # 将 data 中 userprofile 提取 pop 出来，没有就用 {} 代替

        instance = super().update(instance, validated_data)  # 使用 ModelSerializer 自带的 update

        if hasattr(instance, 'userprofile'):
            userprofile = instance.userprofile
        else:
            userprofile = UserProfile(user=instance)
        # 手动更新 userprofile 的每一个值
        userprofile.about = userprofile_data.get('about', userprofile.about)
        userprofile.subscribe_email = userprofile_data.get('subscribe_email', userprofile.subscribe_email)
        userprofile.student_id = userprofile_data.get('student_id', userprofile.student_id)
        userprofile.save()

        return instance


# 作为简单信息的 Serializer，可嵌套于活动签到名单、图片上传者等
class UserBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'avatar_url')
        read_only_fields = ('first_name', 'last_name', 'is_staff', 'is_superuser', 'avatar_url')

    id = serializers.IntegerField()
    avatar_url = serializers.ReadOnlyField(source='userprofile.get_avatar')

    def validate_id(self, id):
        return validate_user_id(id)
