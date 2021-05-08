from django.contrib.auth.models import User, AnonymousUser
from django.db import models
from django.db.models import fields
from django.utils.timezone import now

from cloud.onedrive import OnedriveDriveItem
from cloud.onedrive.api import onedrive_drive


class OnedriveFile(models.Model):
    class Meta:
        abstract = True

    id = fields.CharField(max_length=50, primary_key=True)
    filename = fields.CharField("文件名", max_length=256)
    size = fields.IntegerField("文件大小")
    created_datetime = models.DateTimeField('创建时间', db_index=True)
    thumbnail = fields.CharField("缩略图", max_length=4096)
    download_link = fields.CharField("下载链接", max_length=512)
    uploader = models.ForeignKey(to=User, null=True, on_delete=models.SET_NULL, verbose_name="上传者")

    def __str__(self):
        return self.filename

    # 链接到 onedrive file
    @property
    def driveitem(self) -> OnedriveDriveItem:
        return onedrive_drive.find_file_by_id(self.id)

    # 获取 download_link 等信息
    def collect_info(self):
        self.download_link = self.driveitem.get_download_link()
        self.created_datetime = now()
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
