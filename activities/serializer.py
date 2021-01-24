from django.contrib.auth.models import User
from rest_framework import serializers

from activities.models import Activity  # , Presenter, Attender
from utils.serializer import validate_user_list, validate_userid_list
from users.serializer import UserBriefSerializer


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ("id", "title", "datetime", "location", "presenter", "attender", "check_in_open")

    presenter = UserBriefSerializer(read_only=False, many=True, required=True)
    attender = UserBriefSerializer(read_only=True, many=True)

    # def validate_presenter(self, presenter_list):
    #     validate_user_list(presenter_list)

    def create(self, validated_data):
        presenter_data = validated_data.pop('presenter')
        activity = Activity.objects.create(**validated_data)

        for presenter in presenter_data:
            u = User.objects.get(id=presenter['id'])
            activity.presenter.add(u)

        activity.save()
        return activity

    def update(self, instance: Activity, validated_data):
        presenter_data = validated_data.pop('presenter')
        activity = Activity.objects.update(instance, **validated_data)

        instance.title = validated_data.get('title', instance.title)
        instance.datetime = validated_data.get('datetime', instance.datetime)
        instance.location = validated_data.get('datetime', instance.location)
        instance.check_in_open = validated_data.get('check_in_open', instance.check_in_open)

        instance.presenter.clear()
        for presenter in presenter_data:
            u = User.objects.get(id=presenter['id'])
            activity.presenter.add(u)

        activity.save()
        return activity


class ActivityAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ('check_in_code', )
        read_only_fields = ('check_in_code', )


class ActivityAttenderUpdateSerializer(serializers.Serializer):
    add = serializers.ListSerializer(child=serializers.IntegerField())
    remove = serializers.ListSerializer(child=serializers.IntegerField())

    def validate_add(self, add_list):
        validate_userid_list(add_list)

    def validate_remove(self, remove_list):
        validate_userid_list(remove_list)

    def update(self, instance: Activity, validated_data):
        add_list = validated_data['add']
        remove_list = validated_data['remove']
        add_user_list = User.objects.filter(id__in=add_list)
        remove_user_list = User.objects.filter(id__in=remove_list)
        instance.attender.add(add_user_list)
        instance.attender.remove(remove_user_list)
        instance.save()
        return instance