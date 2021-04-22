from django.contrib.auth.models import User, AnonymousUser
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

    # 根据 Onedrive 响应报文和上传者创建文件，并获取其他信息
    @classmethod
    def create_file(cls, file_info: dict, uploader: User = AnonymousUser, activity_id: int = 0, *args, **kwargs):
        kwargs['activity_id'] = activity_id
        file = super().create_file(file_info, uploader, *args, **kwargs)
        return file
