from django.contrib.auth.models import User
from django.db import models

from activities.models import Activity


class Comment(models.Model):
    class Meta:
        verbose_name = '沙龙留言'
        verbose_name_plural = '沙龙留言'

    activity = models.ForeignKey(Activity, blank=False, on_delete=models.CASCADE, verbose_name="沙龙", db_index=True)
    user = models.ForeignKey(User, blank=False, on_delete=models.CASCADE, verbose_name="留言者", db_index=True, related_name="commenter")
    text = models.CharField(blank=False, max_length=1000, verbose_name="留言内容")
    reply = models.CharField(blank=False, max_length=1000, verbose_name="主讲人回复")
    like = models.ManyToManyField(User, verbose_name="点赞者", related_name="like")

    def like_total(self):
        return self.like.count()

    def __str__(self):
        return  f'{self.user.username}: {self.text} -- {self.activity.title}'