from django.db import models
from activities.models import Activity
from django.contrib.auth.models import User


# Create your models here.
class Photo(models.Model):
    class Meta:
        verbose_name = '图片'
        verbose_name_plural = '图片'

    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, verbose_name="相关沙龙")
    uploader = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="上传者", blank=True)
    url = models.CharField("图片链接", max_length=2000, blank=True)

    def __str__(self):
        return self.url
