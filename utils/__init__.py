import re
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


def is_email(string: str) -> bool:
    email_re = r'^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}$'
    return bool(re.match(email_re, string))


def is_number(string: str) -> bool:
    try:
        int(string)
        return True
    except ValueError:
        return False


def is_valid_username(string: str) -> bool:
    valid_username_re = r'^[a-zA-Z0-9-_]+$'
    return bool(re.match(valid_username_re, string))


class  MyPagination(PageNumberPagination):
    # 指定每一页的个数，默认为配置文件里面的PAGE_SIZE
    page_size =  15

    # 可以让前端指定每页个数，默认为空，这里指定page_size去指定显示个数
    page_size_query_param =  'page_size'

    # 可以让前端指定页码数，默认就是page参数去接收
    page_query_param =  'page'

    # 指定返回格式，根据需求返回一个总页数，数据存在results字典里返回
    def  get_paginated_response(self, data):
        from collections import OrderedDict
        return Response(OrderedDict([('count', self.page.paginator.count), ('results',data)]))