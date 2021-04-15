from django.contrib.auth.models import User
from django.db import models
from django.db.models import fields

from cloud.onedrive import OnedriveDriveItem
from cloud.onedrive.api import onedrive_drive


class OnedriveFile(models.Model):
    class Meta:
        abstract = True

    id = fields.CharField(max_length=50, primary_key=True)
    filename = fields.CharField(max_length=256, verbose_name="文件名")
    thumbnail = fields.CharField(max_length=4096, verbose_name="缩略图")
    download_link = fields.CharField(max_length=512, verbose_name="下载链接")
    uploader = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name="上传者")

    # 链接到 onedrive file
    @property
    def driveitem(self) -> OnedriveDriveItem:
        return onedrive_drive.find_file_by_id(self.id)

    # 获取 thumbnail 和 download_link
    def collect_info(self):
        self.thumbnail = self.driveitem.get_single_thumbnail()
        self.download_link = self.driveitem.get_download_link()
        self.save()


class OnedriveFolder(models.Model):
    class Meta:
        abstract = True

    id = fields.CharField(max_length=50, primary_key=True)

    # 链接到 onedrive file
    @property
    def driveitem(self) -> OnedriveDriveItem:
        return onedrive_drive.find_file_by_id(self.id)