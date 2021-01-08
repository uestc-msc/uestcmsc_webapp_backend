from django.db import models
from django.contrib.auth.models import User
import hashlib
import urllib

# 将 django.contrib.auth.models.User 的 first_name 设为必填
User._meta.get_field('first_name')._Blank = False
User.add_to_class("__str__", lambda u: u.first_name)

# Create your models here.
# 参考 https://www.dusaiphoto.com/article/91/ 使用外链可扩展方式
class UserProfile(models.Model):
    """
    本模型为 django.contrib.auth.models.User 模型的拓展：https://docs.djangoproject.com/en/3.1/ref/contrib/auth/#user-model
    文档：https://github.com/uestc-msc/uestcmsc_webapp_backend/blob/master/docs/develop.md#用户模型-userprofile
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="用户名")
    experience = models.IntegerField("经验", default=0)
    student_id = models.CharField("学号", max_length=20, unique=True)
    about = models.TextField("个性签名", max_length=256, default='')

    def __str__(self) -> str:
        return self.user.username + ' ' + self.student_id

    # https://en.gravatar.com/site/implement/images/django/
    def get_avatar(self, size: int = 40) -> str:
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
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="申请用户")
    token = models.CharField(max_length=32, primary_key=True)
    request_time = models.DateTimeField("申请时间") # 请求重置密码的时间
    ipv4addr = models.CharField("IP 地址", max_length=16) # 请求重置密码的 ip

    def __str__(self) -> str:
        return str(self.user) + " " + str(self.request_time)

    class Meta:
        verbose_name = '重置密码申请'
        verbose_name_plural = '重置密码申请'


