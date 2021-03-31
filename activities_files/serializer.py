from rest_framework import serializers

from .models import ActivityFile
from users.serializer import UserBriefSerializer


class ActivityFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityFile
        fields = ('id', 'activity_id', 'filename', 'thumbnail', 'download_link', 'uploader')
        read_only_fields = fields

    activity_id = serializers.IntegerField(source='activity__id', read_only=True)
    uploader = UserBriefSerializer(read_only=True)
