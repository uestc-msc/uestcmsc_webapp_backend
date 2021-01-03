from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Activity(models.Model):
    class Meta:
        verbose_name = '沙龙'
        verbose_name_plural = '沙龙'

    datetime = models.DateTimeField('日期时间')
    location = models.CharField('地点', max_length=50)
    title = models.CharField('主题', max_length=150)
    attach_link = models.CharField('相关链接', max_length=2000, blank=True)

    def __str__(self):
        return self.title


class Presenter(models.Model):
    class Meta:
        verbose_name = '沙龙主讲人'
        verbose_name_plural = '沙龙主讲人'

    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, verbose_name="活动")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="主讲人")

    def __str__(self):
        return self.user.username + ' ' + self.activity.title


class Attender(models.Model):
    class Meta:
        verbose_name = '沙龙参与者'
        verbose_name_plural = '沙龙参与者'

    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, verbose_name="活动")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="参与者")

    def __str__(self):
        return self.user.username + ' ' + self.activity.title
