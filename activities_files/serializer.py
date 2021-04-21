from rest_framework import serializers, fields

from .models import ActivityFile
from users.serializer import UserBriefSerializer


class ActivityFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityFile
        fields = ('id', 'activity_id', 'filename', 'size', 'thumbnail', 'download_link', 'uploader')
        read_only_fields = fields

    uploader = UserBriefSerializer(read_only=True)
