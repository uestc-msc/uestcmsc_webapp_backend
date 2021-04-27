from django.contrib.auth.models import User
from rest_framework import serializers

from activities.models import Activity
from activities_links.serializer import LinkSerializer
from activities_files.serializer import ActivityFileSerializer
from activities_photos.serializer import ActivityPhotoSerializer
from users.serializer import UserBriefSerializer
from utils.validators import validate_user_id


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ("id", "title", "datetime", "location",
                  "presenter", "attender", "check_in_open",
                  "link", "file", "photo")
        read_only_fields = ("id", "link", "file", "photo")

    title = serializers.CharField(max_length=150)
    location = serializers.CharField(max_length=50)

    # 这样套娃很可能因为活动 presenter、attender 过多导致一个报文太大
    # 但是想了想，俱乐部哪有这么大的活动规模呢
    # 于是懒得改了
    presenter = UserBriefSerializer(read_only=False, many=True)
    attender = UserBriefSerializer(read_only=False, required=False, many=True)
    link = LinkSerializer(read_only=True, many=True)
    file = ActivityFileSerializer(read_only=True, many=True)
    photo = ActivityPhotoSerializer(read_only=True, many=True)

    def validate_presenter(self, presenter_list):
        if len(presenter_list) == 0:
            raise serializers.ValidationError("活动没有演讲者")
        for presenter in presenter_list:
            if 'id' not in presenter:
                raise serializers.ValidationError("用户不包含 id")
            validate_user_id(presenter['id'])
        return presenter_list

    def validate_attender(self, attender_list):
        for presenter in attender_list:
            if 'id' not in presenter:
                raise serializers.ValidationError("用户不包含 id")
            validate_user_id(presenter['id'])
        return attender_list

    def create(self, validated_data):
        presenter_data = validated_data.pop('presenter')
        activity = Activity.objects.create(**validated_data)
        for presenter in presenter_data:
            u = User.objects.get(id=presenter['id'])
            activity.presenter.add(u)
        activity.save()
        return activity

    def update(self, instance: Activity, validated_data):
        if 'presenter' in validated_data:
            presenter_data = validated_data.pop('presenter')
            instance.presenter.clear()
            for presenter in presenter_data:
                u = User.objects.get(id=presenter['id'])
                instance.presenter.add(u)

        if 'attender' in validated_data:
            attender_data = validated_data.pop('attender')
            instance.attender.clear()
            for attender in attender_data:
                u = User.objects.get(id=attender['id'])
                instance.attender.add(u)

        instance = super().update(instance, validated_data)     # 更新 title 等数据
        instance.save()
        return instance


class ActivityAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ('check_in_code', )
        read_only_fields = ('check_in_code', )
