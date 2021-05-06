from typing import Type

from django.forms import CharField
from drf_yasg import openapi
from rest_framework.serializers import Serializer, CharField

# todo 测试通过以后 检查 swagger

# 本文件为简写 @swagger_auto_schema 的语法而生
# drf_yasg 文档：https://drf-yasg.readthedocs.io/en/stable/index.html
# drf_yasg @swagger_auto_schema 函数文档：https://drf-yasg.readthedocs.io/en/1.20.0/drf_yasg.html#drf_yasg.utils.swagger_auto_schema
# 示例：https://zoejoyuliao.medium.com/自定義-drf-yasg-的-swagger-文檔-以-get-post-檔案上傳為例-eeecd922059b


def Schema_array(schema: openapi.Schema) -> openapi.Schema:
    return openapi.Schema(type=openapi.TYPE_ARRAY, items=schema)


def Schema_object(*props: dict) -> openapi.Schema:
    result_properties = {}
    for prop in props:
        result_properties = {**prop, **result_properties}
    return openapi.Schema(type=openapi.TYPE_OBJECT, properties=result_properties)


def Schema_pagination(serializer: Type[Serializer]) -> Serializer:
    class PaginationSerializer(Serializer):
        count = CharField()
        results = serializer(many=True)

    return PaginationSerializer()


Schema_None = None

# 通用
Schema_count = {'count': openapi.Schema(type=openapi.TYPE_NUMBER, description='总数')}
Schema_detail = {'detail': openapi.Schema(type=openapi.TYPE_STRING, description='错误信息')}
Schema_string = {'string': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL)}

# 用户
Schema_email = {'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL, description='邮箱')}
Schema_password = {'password': openapi.Schema(type=openapi.TYPE_STRING, description='密码')}
Schema_token = {'token': openapi.Schema(type=openapi.TYPE_STRING, description='由邮件提供')}
Schema_old_password = {'old_password': openapi.Schema(type=openapi.TYPE_STRING, description='修改者的密码')}
Schema_new_password = {'new_password': openapi.Schema(type=openapi.TYPE_STRING, description='新密码')}
Schema_new_email = {'new_email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL, description='新邮箱')}

# 沙龙
Schema_activity_id = {'activity_id': openapi.Schema(type=openapi.TYPE_NUMBER, description='沙龙 id')}
Schema_title = {'title': openapi.Schema(type=openapi.TYPE_STRING, description='沙龙标题')}
Schema_datetime = {'datetime': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='日期时间')}
Schema_location = {'location': openapi.Schema(type=openapi.TYPE_STRING, description='地点')}
# Schema_presenter_ids = {'presenter': Schema_array(Schema_object(Schema_id))}  # POST 只需要提交 id
Schema_check_in_code = {'check_in_code': openapi.Schema(type=openapi.TYPE_STRING, description='签到码')}
Schema_check_in_open = {'check_in_open': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='管理员开放签到')}
Schema_add = {'add': Schema_array(openapi.Schema(type=openapi.TYPE_NUMBER, description='用户 id'))}
Schema_remove = {'remove': Schema_array(openapi.Schema(type=openapi.TYPE_NUMBER, description='用户 id'))}
Schema_url = {'url': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, description='链接')}

# 云盘
Schema_status = {'status': openapi.Schema(type=openapi.TYPE_STRING, description='状态')}
Schema_file_id = {'file_id': openapi.Schema(type=openapi.TYPE_STRING, description='文件 id')}
Schema_filename = {'filename': openapi.Schema(type=openapi.TYPE_STRING, description='文件名')}

Param_search = openapi.Parameter('search', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='搜索关键字（为空时表示不搜索）')
Param_page = openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_NUMBER, description='页数（不正确时返回 404）')
Param_page_size = openapi.Parameter('page_size', openapi.IN_QUERY, type=openapi.TYPE_NUMBER,
                                    description='页大小（不为正数时表示不分页）')
