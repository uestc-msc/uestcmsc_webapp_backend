import uuid
from datetime import datetime
from random import randrange

import pytz
from rest_framework.pagination import PageNumberPagination

from uestcmsc_webapp_backend.settings import TIME_ZONE


# 判断两个 aware datetime 在 settings.TIME_ZONE 下是否是同一天
def compare_date(dt1: datetime, dt2: datetime) -> bool:
    tz = pytz.timezone(TIME_ZONE)
    return dt1.astimezone(tz).date() == dt2.astimezone(tz).date()


# 基于 Django REST Framework 的分页器
class Pagination(PageNumberPagination):
    page_size = 15  # 默认页大小
    page_size_query_param = 'page_size'  # 页大小的参数名
    page_query_param = 'page'  # 页码数的参数名
