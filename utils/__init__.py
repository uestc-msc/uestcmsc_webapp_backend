import re
import uuid
from random import randrange

from rest_framework.pagination import PageNumberPagination

# 判断字符串是否为邮箱


def is_email(string: str) -> bool:
    email_re = r'^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}$'
    return bool(re.match(email_re, string))


# 判断密码是否合法（依据文档：https://github.com/uestc-msc/uestcmsc_webapp_backend/blob/master/docs/develop.md#用户模型-userprofile）
def is_valid_password(string: str)-> bool:
    return len(string) >= 6


# 判断字符串是否为数字
def is_number(string: str) -> bool:
    try:
        int(string)
        return True
    except ValueError:
        return False


# 生成一个 32 位 uuid
def generate_uuid() -> str:
    return str(uuid.uuid1()).replace('-', '')


# 生成一个由 5 位大写字母组成的随机字符串，作为活动签到凭据
def generate_check_in_code() -> str:
    while True:
        code = ''
        lb = ord('A')
        ub = ord('Z') + 1
        for i in range(5):
            code += chr(randrange(lb, ub))
        from activities.models import Activity
        if not Activity.objects.filter(check_in_code=code):
            break
    return code


# 基于 Django REST Framework 的分页器
class MyPagination(PageNumberPagination):
    page_size = 15                          # 默认页大小
    page_size_query_param = 'page_size'     # 页大小的参数名
    page_query_param = 'page'               # 页码数的参数名


