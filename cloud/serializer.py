from rest_framework import serializers

from cloud.models import OnedriveFile


class OnedriveFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnedriveFile
        fields = ('id', 'filename', 'size', 'thumbnail', 'download_link', 'uploader_id')
        read_only_fields = fields

