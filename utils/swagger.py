from functools import reduce
from typing import List

from drf_yasg import openapi


# 本文件为简写 @swagger_auto_schema 的语法而生
# drf_yasg 文档：https://drf-yasg.readthedocs.io/en/stable/index.html
# 参考：https://zoejoyuliao.medium.com/自定義-drf-yasg-的-swagger-文檔-以-get-post-檔案上傳為例-eeecd922059b

def Schema_object(*prop: List[dict]) -> openapi.Schema:
    def merge_two_dict(x: dict, y: dict) -> dict:
        return {**x, **y}
    return openapi.Schema(type=openapi.TYPE_OBJECT, properties=reduce(merge_two_dict, prop))


Schema_string = {"string": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL)}
Schema_email = {"email": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL, description='邮箱')}
Schema_password = {"password": openapi.Schema(type=openapi.TYPE_STRING, description='密码')}
Schema_token = {'token': openapi.Schema(type=openapi.TYPE_STRING, description='由邮件提供')}
Schema_old_password = {'old_password': openapi.Schema(type=openapi.TYPE_STRING, description='旧密码')}
Schema_new_password = {'new_password': openapi.Schema(type=openapi.TYPE_STRING, description='新密码')}
