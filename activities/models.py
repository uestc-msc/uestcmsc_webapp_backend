from django.db import models
from django.contrib.auth.models import User
from utils import generate_check_in_code


class Activity(models.Model):
    class Meta:
        verbose_name = '沙龙'
        verbose_name_plural = '沙龙'

    datetime = models.DateTimeField('日期时间', db_index=True)
    location = models.CharField('地点', max_length=50)
    title = models.CharField('主题', max_length=150)
    check_in_code = models.CharField('签到码', max_length=10, db_index=True, default=generate_check_in_code)
    presenter = models.ManyToManyField(User, through='Presenter', verbose_name="主讲人", related_name="activity_presenter")
    attender = models.ManyToManyField(User, through='Attender', verbose_name="参与者", related_name="activity_attender")

    def __str__(self):
        return self.title

    def attender_count(self): # 返回参与者数量
        return self.attender_set.count()


class Presenter(models.Model):
    class Meta:
        verbose_name = '沙龙主讲人'
        verbose_name_plural = '沙龙主讲人'

    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, verbose_name="沙龙", db_index=True, related_name='activity_presenter')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="主讲人", db_index=True)

    def __str__(self):
        return self.user.username + ' ' + self.activity.title


class Attender(models.Model):
    class Meta:
        verbose_name = '沙龙参与者'
        verbose_name_plural = '沙龙参与者'

    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, verbose_name="沙龙", db_index=True, related_name='activity_attender')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="参与者", db_index=True)

    def __str__(self):
        return self.user.username + ' ' + self.activity.title


class ActivityRelatedLink(models.Model):
    class Meta:
        verbose_name = '沙龙相关链接'
        verbose_name_plural = '沙龙相关链接'

    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, verbose_name="沙龙", db_index=True)
    url = models.CharField('相关链接', max_length=2000, blank=True)

