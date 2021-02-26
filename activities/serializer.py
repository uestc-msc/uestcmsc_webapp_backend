from django.contrib.auth.models import User
from rest_framework import serializers

from activities.models import Activity  # , Presenter, Attender
from users.serializer import UserBriefSerializer
from utils.validators import validate_user_id


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ("id", "title", "datetime", "location", "presenter", "attender", "check_in_open")

    title = serializers.CharField(max_length=150)
    location = serializers.CharField(max_length=50)
    presenter = UserBriefSerializer(read_only=False, many=True)
    attender = UserBriefSerializer(read_only=True, many=True)

    def validate_presenter(self, presenter_list):
        if len(presenter_list) == 0:
            raise serializers.ValidationError("活动没有演讲者")
        for presenter in presenter_list:
            if 'id' not in presenter:
                raise serializers.ValidationError("用户不包含 id")
            validate_user_id(presenter['id'])
        return presenter_list

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

        instance = super().update(instance, validated_data) # 更新 title 等数据
        instance.save()
        return instance


class ActivityAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ('check_in_code', )
        read_only_fields = ('check_in_code', )
