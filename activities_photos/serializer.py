from activities_files.serializer import ActivityFileSerializer
from .models import ActivityPhoto


# 序列化器也复用 ActivityFileSerializer
class ActivityPhotoSerializer(ActivityFileSerializer):
    class Meta:
        model = ActivityPhoto
        fields = ('id', 'activity_id', 'filename', 'size', 'created_datetime', 'download_link', 'uploader_id')
        read_only_fields = fields
