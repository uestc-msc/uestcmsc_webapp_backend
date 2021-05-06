from rest_framework import serializers

from .models import ActivityFile


class ActivityFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityFile
        fields = ('id', 'activity_id', 'filename', 'size', 'download_link', 'uploader_id')
        read_only_fields = fields
