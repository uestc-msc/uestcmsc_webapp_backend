from rest_framework import serializers

from cloud.models import OnedriveFile
from users.serializer import UserBriefSerializer


class OnedriveFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnedriveFile
        fields = ('id', 'filename', 'thumbnail', 'download_link', 'uploader')
        read_only_fields = fields

    uploader = UserBriefSerializer(read_only=True)