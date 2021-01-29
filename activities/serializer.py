from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.serializers import ListSerializer

from activities.models import Activity  # , Presenter, Attender
from utils.serializer import *
from users.serializer import UserBriefSerializer


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ("id", "title", "datetime", "location", "presenter", "attender", "check_in_open")

    presenter = UserBriefSerializer(read_only=False, many=True, required=True)
    attender = UserBriefSerializer(read_only=True, many=True)

    def validate_presenter(self, presenter_list):
        if len(presenter_list) == 0:
            raise serializers.ValidationError("演讲者名单不应为空")
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


class ActivityAttenderUpdateSerializer(serializers.Serializer):
    add = serializers.ListSerializer(child=serializers.IntegerField())
    remove = serializers.ListSerializer(child=serializers.IntegerField())

    def validate_add(self, add_list):
        for user_id in add_list:
            validate_user_id(user_id)
        return add_list

    def validate_remove(self, remove_list):
        for user_id in remove_list:
            validate_user_id(user_id)
        return remove_list

    def update(self, instance: Activity, validated_data):
        add_list = validated_data['add']
        remove_list = validated_data['remove']
        add_user_list = User.objects.filter(id__in=add_list)
        remove_user_list = User.objects.filter(id__in=remove_list)
        instance.attender.add(add_user_list)
        instance.attender.remove(remove_user_list)
        instance.save()
        return instance