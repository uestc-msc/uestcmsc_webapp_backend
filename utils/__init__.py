import re
import uuid
from random import randrange

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


# 判断字符串是否为邮箱
def is_email(string: str) -> bool:
    email_re = r'^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}$'
    return bool(re.match(email_re, string))


# 判断密码是否合法（依据文档：https://github.com/uestc-msc/uestcmsc_webapp_backend/blob/master/docs/develop.md#用户模型-userprofile）
def is_valid_password(string: str)-> bool:
    return  len(string) >= 6


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


# 生成一个由 5 位大写字母组成的随机字符串
def generate_check_in_code():
    code = ''
    lb = ord('A')
    ub = ord('Z') + 1
    for i in range(5):
        code += chr(randrange(lb, ub))
    return code

# 基于 Django REST Framework 的分页器
class MyPagination(PageNumberPagination):
    # 指定每一页的个数，默认为配置文件里面的PAGE_SIZE
    page_size = 15

    # 可以让前端指定每页个数，默认为空，这里指定page_size去指定显示个数
    page_size_query_param = 'page_size'

    # 可以让前端指定页码数，默认就是page参数去接收
    page_query_param = 'page'

    # 指定返回格式，根据需求返回一个总页数，数据存在results字典里返回
    def get_paginated_response(self, data):
        from collections import OrderedDict
        return Response(OrderedDict([('count', self.page.paginator.count), ('results',data)]))

