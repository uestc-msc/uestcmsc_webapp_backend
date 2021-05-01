import requests
from django.contrib.auth.models import User, AnonymousUser
from django.db import models
from django.db.models import fields

from cloud.onedrive import OnedriveDriveItem, OnedriveUnavailableException
from cloud.onedrive.api import onedrive_drive
from cloud.onedrive.api.request import log_onedrive_error


class OnedriveFile(models.Model):
    class Meta:
        abstract = True

    id = fields.CharField(max_length=50, primary_key=True)
    filename = fields.CharField(max_length=256, verbose_name="文件名")
    size = fields.IntegerField(verbose_name="文件大小")
    thumbnail = fields.CharField(max_length=4096, verbose_name="缩略图")
    download_link = fields.CharField(max_length=512, verbose_name="下载链接")
    uploader = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name="上传者")

    def __str__(self):
        return self.filename

    # 链接到 onedrive file
    @property
    def driveitem(self) -> OnedriveDriveItem:
        return onedrive_drive.find_file_by_id(self.id)

    # 获取 download_link
    def collect_info(self):
        self.download_link = self.driveitem.get_download_link()
        self.save()

    # 根据 Onedrive 响应报文和上传者创建文件，并获取其他信息
    @classmethod
    def create_file(cls, file_info: dict, uploader: User = AnonymousUser, *args, **kwargs):
        file = cls(**kwargs)
        file.id = file_info['id']
        file.filename = file_info['name']
        file.size = file_info['size']
        file.uploader = uploader
        file.collect_info()
        return file


class OnedriveFolder(models.Model):
    class Meta:
        abstract = True

    id = fields.CharField(max_length=50, primary_key=True)

    # 链接到 onedrive file
    @property
    def driveitem(self) -> OnedriveDriveItem:
        return onedrive_drive.find_file_by_id(self.id)