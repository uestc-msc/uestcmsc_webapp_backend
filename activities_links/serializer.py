from rest_framework import serializers

from .models import ActivityLink


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLink
        fields = ("id", "activity_id", "url")
        read_only_fields = ("id", "activity_id")
        # TODO 测试返回字段是否有 activity_id

    url = serializers.CharField(max_length=512, required=True)
    activity_id = serializers.IntegerField(read_only=True)
