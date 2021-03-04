from django.contrib.auth.models import User
from django.db import models
from django.db.models import fields


class OnedriveFile(models.Model):
    class Meta:
        abstract = True

    id = fields.CharField(max_length=50, primary_key=True)
    filename = fields.CharField(max_length=256, verbose_name="文件名")
    thumbnail = fields.CharField(max_length=4096, verbose_name="缩略图")
    download_link = fields.CharField(max_length=512, verbose_name="下载链接")
    uploader = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name="上传者")


class OnedriveFolder(models.Model):
    class Meta:
        abstract = True

    id = fields.CharField(max_length=50, primary_key=True)