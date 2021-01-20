from rest_framework import serializers
from rest_framework.fields import ListField

from activities.models import Activity, Presenter, Attender


class PresenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Presenter
        fields = ('pk', 'first_name', 'second_name')

    pk = serializers.CharField(source='user.pk')
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    second_name = serializers.CharField(source='user.second_name', read_only=True)


class AttenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attender
        fields = ('pk', 'first_name', 'second_name')

    pk = serializers.CharField(source='user.pk')
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    second_name = serializers.CharField(source='user.second_name', read_only=True)


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        exclude = ('check_in_code',)

    presenter = PresenterSerializer(many=True)
    attender = serializers.CharField(read_only=True)

