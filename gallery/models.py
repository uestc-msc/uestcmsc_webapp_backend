from django.db import models

from activities.models import Activity
from cloud.models import OnedriveFile


class ActivityPhoto(OnedriveFile):
    class Meta:
        verbose_name = '沙龙照片'
        verbose_name_plural = '沙龙照片'
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, verbose_name="沙龙",
                                 db_index=True, related_name="photo")