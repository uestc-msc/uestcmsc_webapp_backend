from typing import List

from rest_framework import serializers

from activities.models import Activity
from activities_files.serializer import ActivityFileSerializer
from activities_links.serializer import LinkSerializer
from activities_photos.models import ActivityPhoto
from activities_photos.serializer import ActivityPhotoSerializer
from utils.validators import validate_user_ids


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ("id", "title", "datetime", "location",
                  "presenter", "attender", "check_in_open",
                  "link", "file", "banner_id")
        read_only_fields = ("id", "attender", "link", "file", "photo")

    title = serializers.CharField(max_length=150)
    location = serializers.CharField(max_length=50)

    presenter = serializers.ListField(child=serializers.IntegerField(), source='presenter_id', read_only=False)
    # 不能通过 PATCH activity 提交 attender，否则修改名单时签到的同学会被覆盖
    # 必须使用 PATCH /activities/{id}/attender/ 增量更新名单
    attender = serializers.ListField(child=serializers.IntegerField(), source='attender_id', read_only=True)
    link = LinkSerializer(read_only=True, many=True)
    file = ActivityFileSerializer(read_only=True, many=True)
    # 图片可能因为过多导致一个 activity 的 json 过大
    # photo = ActivityPhotoSerializer(read_only=True, many=True)
    banner_id = serializers.CharField(allow_null=True, read_only=False)

    def validate_presenter(self, presenter: List[int]):
        if len(presenter) == 0:
            raise serializers.ValidationError("活动没有演讲者")
        validate_user_ids(presenter)
        return presenter

    def validate_banner_id(self, banner_id: str):
        if banner_id is None or ActivityPhoto.objects.filter(id=banner_id):
            return banner_id
        raise serializers.ValidationError("id 对应的图片不存在")

    def create(self, validated_data):
        presenter_id = validated_data.pop('presenter_id', [])
        activity = super().create(validated_data)
        activity.presenter_id = presenter_id
        return activity


class ActivityAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ('check_in_code', )
        read_only_fields = ('check_in_code', )
