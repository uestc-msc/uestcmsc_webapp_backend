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
    models.User 类：https://docs.djangoproject.com/en/3.1/ref/contrib/auth/#fields
    本模型为 User 模型的拓展。使用了 User 模型的：
    username（用户名）
    first_name（姓名）
    email（邮箱）
    password（密码）
    is_active（未被删除）
    is_staff（管理员）
    is_superuser（超级管理员）
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="用户名")
    experience = models.IntegerField("经验值", default=0)
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
