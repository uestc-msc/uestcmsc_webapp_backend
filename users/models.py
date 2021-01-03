from django.db import models
from django.contrib.auth.models import User
import hashlib
import urllib


# Create your models here.
# 参考 https://www.dusaiphoto.com/article/91/ 使用外链可扩展方式
# models.User 类：https://docs.djangoproject.com/en/3.1/ref/contrib/auth/#fields
class UserProfile(models.Model):
    class Meta:
        verbose_name = '用户其他信息'
        verbose_name_plural = '用户其他信息'

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="用户名")
    experience = models.IntegerField("经验值", default=0)
    student_id = models.CharField("学号", max_length=20)

    def __str__(self):
        return self.user.username + ' ' + self.student_id

    # https://en.gravatar.com/site/implement/images/django/
    def get_avatar(self, size=40):
        email = self.user.email
        default = "https://example.com/static/images/defaultavatar.jpg"
        return "https://www.gravatar.com/avatar/%s?%s" % (
        hashlib.md5(email.lower()).hexdigest(), urllib.urlencode({'d': default, 's': str(size)}))
