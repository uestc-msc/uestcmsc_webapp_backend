import re


def is_email(string: str) -> bool:
    email_re = r'^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}$'
    return bool(re.match(email_re, string))


def is_number(string: str) -> bool:
    try:
        int(string)
        return True
    except ValueError:
        return False
