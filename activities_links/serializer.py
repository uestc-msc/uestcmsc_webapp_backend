from rest_framework import serializers

from .models import ActivityLink


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLink
        fields = ("id", "url")

    url = serializers.CharField(max_length=512, required=True)
