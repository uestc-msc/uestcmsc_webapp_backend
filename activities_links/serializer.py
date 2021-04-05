from rest_framework import serializers

from .models import ActivityLink


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLink
        fields = ("id", "url")
        read_only_fields = ("id", )

    url = serializers.CharField(max_length=512, required=True)
