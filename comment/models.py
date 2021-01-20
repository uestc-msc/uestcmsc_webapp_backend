from django.contrib.auth.models import User
from django.db import models

from activities.models import Activity


class Comment(models.Model):
    class Meta:
        verbose_name = '沙龙留言'
        verbose_name_plural = '沙龙留言'

    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, verbose_name="沙龙", db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="留言者", db_index=True)
    text = models.CharField(blank=False, max_length=1000, verbose_name="留言内容")
    reply = models.CharField(blank=False, max_length=1000, verbose_name="主讲人回复")

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