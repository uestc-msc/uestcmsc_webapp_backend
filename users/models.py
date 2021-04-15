from django.contrib.auth.models import User
from django.db import models
from libgravatar import Gravatar

from uestcmsc_webapp_backend.settings import USER_DEFAULT_AVATAR

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

    class Meta:
        verbose_name = '用户其他信息'
        verbose_name_plural = '用户其他信息'

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="用户名", db_index=True)
    experience = models.IntegerField("经验", default=0)
    student_id = models.CharField("学号", max_length=20, unique=True, blank=True)
    about = models.TextField("自我介绍", max_length=256, default='', blank=True)
    subscribe_email = models.BooleanField("接收邮件", default=True, blank=True)
    subscribe_system_alter_email = models.BooleanField("接收系统警告邮件（仅超级用户有效）", default=False, blank=True)

    def __str__(self) -> str:
        return self.user.first_name + ' ' + self.student_id

    # https://libgravatar.readthedocs.io/en/latest/
    def get_avatar(self, size: int = 300) -> str:
        return Gravatar(self.user.username).get_image(size=size,
                                                      default=USER_DEFAULT_AVATAR,
                                                      use_ssl=True)


class ResetPasswordRequest(models.Model):
    """
    本模型存储了申请重置密码的用户信息
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="申请用户")
    token = models.CharField(max_length=32, primary_key=True, db_index=True)
    request_time = models.DateTimeField("申请时间", db_index=True)  # 请求重置密码的时间
    ipv4addr = models.CharField("IP 地址", max_length=16, db_index=True)  # 请求重置密码的 ip

    def __str__(self) -> str:
        return str(self.user) + " " + str(self.request_time)

    class Meta:
        verbose_name = '重置密码申请'
        verbose_name_plural = '重置密码申请'
