from django.db import models
from activities.models import Activity
from cloud.models import OnedriveFolder, OnedriveFile


class ActivityFolder(OnedriveFolder):
    class Meta:
        verbose_name = '沙龙文件夹'
        verbose_name_plural = '沙龙文件夹'

    activity = models.OneToOneField(Activity, on_delete=models.CASCADE, verbose_name="沙龙",
                                    db_index=True, related_name="folder")


class ActivityFile(OnedriveFile):
    class Meta:
        verbose_name = '沙龙文件'
        verbose_name_plural = '沙龙文件'

    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, verbose_name="沙龙",
                                 db_index=True, related_name="file")
