from django.db import models
from django.contrib.auth.models import User
import hashlib
import urllib

# 将 django.contrib.auth.models.User 的 email 成员设为唯一、first_name 设为必填
User._meta.get_field('email')._unique = True
User._meta.get_field('first_name')._Blank = False


# Create your models here.
# 参考 https://www.dusaiphoto.com/article/91/ 使用外链可扩展方式
class UserProfile(models.Model):
    """
    本模型为 django.contrib.auth.models.User 模型的拓展。
    文档：/docs/develop.md#用户模型-userprofile
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="用户名")
    email_public = models.BooleanField(default=False, verbose_name="将邮箱设为公开")
    experience = models.IntegerField("经验", default=0)
    student_id = models.CharField("学号", max_length=20, unique=True)

    def __str__(self):
        return self.user.username + ' ' + self.student_id

    # https://en.gravatar.com/site/implement/images/django/
    def get_avatar(self, size=40):
        email = self.user.email
        default = "https://example.com/static/images/defaultavatar.jpg"
        return "https://www.gravatar.com/avatar/%s?%s" % (
            hashlib.md5(email.lower()).hexdigest(), urllib.urlencode({'d': default, 's': str(size)}))

    class Meta:
        verbose_name = '用户其他信息'
        verbose_name_plural = '用户其他信息'


class ResetPasswordRequest(models.Model):
    """
    本模型存储了申请重置密码的用户信息
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户名")
    token = models.CharField(max_length=32)
    request_time = models.DateTimeField(auto_now_add=True) # 请求重置密码的时间
