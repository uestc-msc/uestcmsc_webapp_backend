from django.db import models
from django.contrib.auth.models import User
from utils import generate_check_in_code

# Create your models here.
class Activity(models.Model):
    class Meta:
        verbose_name = '沙龙'
        verbose_name_plural = '沙龙'

    datetime = models.DateTimeField('日期时间', db_index=True)
    location = models.CharField('地点', max_length=50)
    title = models.CharField('主题', max_length=150)
    check_in_code = models.CharField('签到码', max_length=10, db_index=True, default=generate_check_in_code)
    attach_link = models.CharField('相关链接', max_length=2000, blank=True)

    def __str__(self):
        return self.title


class Presenter(models.Model):
    class Meta:
        verbose_name = '沙龙主讲人'
        verbose_name_plural = '沙龙主讲人'

    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, verbose_name="活动", db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="主讲人", db_index=True)

    def __str__(self):
        return self.user.username + ' ' + self.activity.title


class Attender(models.Model):
    class Meta:
        verbose_name = '沙龙参与者'
        verbose_name_plural = '沙龙参与者'

    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, verbose_name="活动", db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="参与者", db_index=True)

    def __str__(self):
        return self.user.username + ' ' + self.activity.title


class Comment(models.Model):
    class Meta:
        verbose_name = '沙龙留言'
        verbose_name_plural = '沙龙留言'

    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, verbose_name="活动", db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="留言者", db_index=True)
    text = models.CharField(blank=False, max_length=1000, verbose_name="留言内容")
    reply = models.CharField(blank=False, max_length=1000, verbose_name="留言内容")

    def __str__(self):
        return self.activity.title + ' ' + self.user.username + ' ' + self.text


class CommentLike(models.Model):
    class Meta:
        verbose_name = '留言点赞'
        verbose_name_plural = '留言点赞'

    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, verbose_name="留言", db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="点赞者")

    def __str__(self):
        return self.comment.__str__()
