from django.test import Client
from django.http import response
from django.http.response import HttpResponse

HTTP_USER_AGENT = 'Mozilla/5.0'


def tester_signup(username: str = "admin@example.com",
                  password: str = "adminadmin",
                  first_name: str = 'admin',
                  student_id: str = "20210101",
                  c: Client = Client(HTTP_USER_AGENT=HTTP_USER_AGENT)) -> response:
    """
    测试时用于创建一个默认账户。也可以用于给定参数创建账户
    """
    return c.post('/users/', {
        'username': username,
        'password': password,
        'first_name': first_name,
        'student_id': student_id
    })


def tester_login(username: str = 'admin@example.com',
                 password: str = "adminadmin",
                 c: Client = Client(HTTP_USER_AGENT=HTTP_USER_AGENT)) -> response:
    """
    测试时用于登录一个默认账户。也可以用于给定参数登录指定账户
    """
    return c.post('/users/login/', {
        'username': username,
        'password': password
    })
