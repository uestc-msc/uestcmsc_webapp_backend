import re


# 判断字符串是否为邮箱
def is_email(string: str) -> bool:
    email_re = r'^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}$'
    return bool(re.match(email_re, string))


# 判断密码是否合法
def is_valid_password(string: str)-> bool:
    return len(string) >= 6


# 判断字符串是否为数字
def is_number(string: str) -> bool:
    try:
        int(string)
        return True
    except ValueError:
        return False