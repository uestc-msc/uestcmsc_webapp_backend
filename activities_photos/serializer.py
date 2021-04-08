from activities_files.serializer import ActivityFileSerializer
from .models import ActivityPhoto


# 序列化器也复用 ActivityFileSerializer
class ActivityPhotoSerializer(ActivityFileSerializer):
    class Meta:
        model = ActivityPhoto
