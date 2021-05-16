from typing import List

from django.db import models
from django.contrib.auth.models import User

from cloud.models import OnedriveFile, OnedriveFolder
from utils.random import generate_check_in_code


class Activity(models.Model):
    class Meta:
        verbose_name = '沙龙'
        verbose_name_plural = '沙龙'

    datetime = models.DateTimeField('日期时间',db_index=True, )
    location = models.CharField('地点', max_length=50)
    title = models.CharField('主题', max_length=150)
    check_in_code = models.CharField('签到码', max_length=10, db_index=True, default=generate_check_in_code)
    check_in_open = models.BooleanField('开放签到', default=True)
    presenter = models.ManyToManyField(User, verbose_name="主讲人", related_name="present_activity")
    attender = models.ManyToManyField(User, verbose_name="参与者", related_name="attend_activity")
    banner = models.ForeignKey('activities_photos.ActivityPhoto', null=True, default=None, on_delete=models.SET_NULL,
                               verbose_name="封面", related_name="banner_of")

    def __str__(self):
        return self.title

    @property
    def presenter_id(self) -> List[int]:
        queryset = self.presenter.all().values('id')
        return list(map(lambda u: u['id'], queryset))

    @presenter_id.setter
    def presenter_id(self, value: List[int]):
        self.presenter.clear()
        self.presenter.add(*value)

    # 为防止 presenter 直接修改数据覆盖 attender 的签到记录，不提供 attender 的 setter，只提供 getter
    @property
    def attender_id(self) -> List[int]:
        queryset = self.attender.all().values('id')
        return list(map(lambda u: u['id'], queryset))
