from functools import reduce
from typing import Dict, Type

from django.forms import CharField
from drf_yasg import openapi
from drf_yasg.inspectors import SerializerInspector
from rest_framework import serializers
from rest_framework.fields import DecimalField

from rest_framework.serializers import Serializer, CharField

# 本文件为简写 @swagger_auto_schema 的语法而生
# drf_yasg 文档：https://drf-yasg.readthedocs.io/en/stable/index.html
# drf_yasg @swagger_auto_schema 函数文档：https://drf-yasg.readthedocs.io/en/1.20.0/drf_yasg.html#drf_yasg.utils.swagger_auto_schema
# 示例：https://zoejoyuliao.medium.com/自定義-drf-yasg-的-swagger-文檔-以-get-post-檔案上傳為例-eeecd922059b


def Schema_object(*prop: dict) -> openapi.Schema:
    def merge_two_dict(x: dict, y: dict) -> dict:
        return {**x, **y}
    return openapi.Schema(type=openapi.TYPE_OBJECT, properties=reduce(merge_two_dict, prop))


def Schema_pagination(serializer: Type[Serializer]) -> Type[Serializer]:
    class PaginationSerializer(Serializer):
        count = CharField()
        results = serializer(many=True)
    return PaginationSerializer


Schema_string = {"string": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL)}
Schema_email = {"email": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL, description='邮箱')}
Schema_password = {"password": openapi.Schema(type=openapi.TYPE_STRING, description='密码')}
Schema_token = {'token': openapi.Schema(type=openapi.TYPE_STRING, description='由邮件提供')}
Schema_old_password = {'old_password': openapi.Schema(type=openapi.TYPE_STRING, description='旧密码')}
Schema_new_password = {'new_password': openapi.Schema(type=openapi.TYPE_STRING, description='新密码')}
Schema_count = {"count": openapi.Schema(type=openapi.TYPE_NUMBER, description="总数")}



Param_keyword = openapi.Parameter("keyword", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='关键字')
Param_page = openapi.Parameter("page", openapi.IN_QUERY, type=openapi.TYPE_NUMBER, description='页数')
Param_page_size = openapi.Parameter("page_size", openapi.IN_QUERY, type=openapi.TYPE_NUMBER, description='页大小')


