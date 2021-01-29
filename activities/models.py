from django.db import models
from django.contrib.auth.models import User
from utils import generate_check_in_code


class Activity(models.Model):
    class Meta:
        verbose_name = '沙龙'
        verbose_name_plural = '沙龙'

    datetime = models.DateTimeField('日期时间', db_index=True, )
    location = models.CharField('地点', max_length=50)
    title = models.CharField('主题', max_length=150)
    check_in_code = models.CharField('签到码', max_length=10, db_index=True, default=generate_check_in_code)
    check_in_open = models.BooleanField('开放签到', default=True)
    presenter = models.ManyToManyField(User, verbose_name="主讲人", related_name="activity_presenter")
    attender = models.ManyToManyField(User, verbose_name="参与者", related_name="activity_attender")

    def __str__(self):
        return self.title


class ActivityURL(models.Model):
    class Meta:
        verbose_name = '沙龙相关链接'
        verbose_name_plural = '沙龙相关链接'

    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, verbose_name="沙龙")
    url = models.CharField('相关链接', max_length=2000, blank=True)
