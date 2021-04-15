import uuid

from django.utils.crypto import get_random_string


# 生成一个 32 位 uuid
def generate_uuid() -> str:
    return str(uuid.uuid1()).replace('-', '')


# 生成一个 5 位随机字符串，作为活动签到凭据
def generate_check_in_code() -> str:
    while True:
        code = get_random_string(length=5, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        from activities.models import Activity
        if not Activity.objects.filter(check_in_code=code):
            break
    return code

