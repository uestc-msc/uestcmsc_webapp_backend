import uuid

from random import randrange


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

