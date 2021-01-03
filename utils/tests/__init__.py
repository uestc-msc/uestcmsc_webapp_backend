from django.test import Client
from django.http import response


def tester_signup(username: str = 'admin',
                  password: str = "adminadmin",
                  first_name: str = 'admin',
                  email: str = "admin@example.com",
                  student_id: str = "20210101") -> response:
    """
    测试时用于创建一个默认账户。也可以用于给定参数创建账户
    """
    c = Client(HTTP_USER_AGENT='Mozilla/5.0')
    return c.post('/users/signup/', {
        'username': username,
        'password': password,
        'first_name': first_name,
        'email': email,
        'student_id': student_id
    })
