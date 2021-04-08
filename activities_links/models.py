from django.db import models

# Create your models here.
from activities.models import Activity


class ActivityLink(models.Model):
    class Meta:
        verbose_name = '相关链接'
        verbose_name_plural = '相关链接'

    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, verbose_name="沙龙",
                                 db_index=True, related_name="link")
    url = models.CharField('相关链接', max_length=512)

    def __str__(self):
        return self.url