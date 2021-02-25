import json
import re
from datetime import datetime, timedelta
from typing import Union, List, Dict
from unittest import TestCase

from django.contrib.auth.models import User
from django.core import mail
from django.http import response
from django.test import Client
from django.urls import reverse

from activities.models import Activity
from activities.serializer import ActivitySerializer
from users.serializer import UserSerializer, UserBriefSerializer

HTTP_USER_AGENT = 'Mozilla/5.0'

############################################


def tester_signup(username: str = "admin@example.com",
                  password: str = "adminadmin",
                  first_name: str = 'admin',
                  student_id: str = "20210101",
                  client: Client = Client(HTTP_USER_AGENT=HTTP_USER_AGENT)) -> response:
    """
    测试时用于创建一个默认账户。也可以用于给定参数创建账户
    """
    url = reverse('signup')
    return client.post(url, {
        'username': username,
        'password': password,
        'first_name': first_name,
        'student_id': student_id
    })


def tester_login(username: str = 'admin@example.com',
                 password: str = "adminadmin",
                 client: Client = Client(HTTP_USER_AGENT=HTTP_USER_AGENT)) -> response:
    """
    测试时用于登录一个默认账户。也可以用于给定参数登录指定账户
    """
    url = reverse('login')
    return client.post(url, {
        'username': username,
        'password': password
    })


def tester_create_activity(title: str = "测试沙龙",
                    date_time: Union[str, datetime] = "2021-01-01T08:00:00.000+08:00",
                    location: str = "GitHub",
                    presenter_ids: List[int] = None,
                    client: Client = None) -> response:
    """
    测试时用于创建一个默认活动。也可以用于给定参数创建活动
    """
    if client is None:
        client = Client(HTTP_USER_AGENT=HTTP_USER_AGENT)
        tester_signup(client=client)
        tester_login(client=client)
    if presenter_ids is None:
        presenter_ids = [User.objects.first().id]
    presenter = list(map(lambda id: {"id": id}, presenter_ids))
    url = reverse('activity_list')
    data = {
        'title': title,
        'datetime': date_time,
        'location': location,
        'presenter': presenter
    }

    return client.post(url, data, content_type='application/json')

#################################################


def pop_token_from_virtual_mailbox(test_function):
    """
    测试时从虚拟的邮箱中找到验证码，并清空测试发件箱
    虚拟邮箱：https://docs.djangoproject.com/zh-hans/3.1/topics/testing/tools/#email-services
    """
    test_function.assertEqual(len(mail.outbox), 1)
    message = mail.outbox[0].message().as_string()
    mail.outbox = []
    token = re.findall('token=.+', message)[0][6:]
    return token

##################################################


def assertDatetimeEqual(cls: TestCase, dt1: Union[datetime, str], dt2: datetime):
    """
    比较两个时间是否在误差 1s 内相等（因为 Django 模型的 datetime 只精确到 1ms）
    """
    if dt1 is None:
        return dt2 is None
    if type(dt1) is str:
        dt1 = datetime.fromisoformat(dt1)
    cls.assertLess(abs(dt1 - dt2), timedelta(seconds=1), f"{dt1}!={dt2}")


def assertUserDetailEqual(cls: TestCase, content: str, user: User):
    """
    比较 REST API 返回的 User 和数据库中 User 是否相同
    """
    compare_fields = set(UserSerializer.Meta.fields) - {'last_login', 'date_joined', 'username', 'student_id'}  # 时间正确性不能通过字符串比较
    json1 = json.loads(content)
    json2 = UserSerializer(user).data
    for field in compare_fields:
        cls.assertEqual(json1[field], json2[field])  # 获取的数据和数据库中的数据在 json 意义上等价

    assertDatetimeEqual(cls, json1['date_joined'], user.date_joined)
    assertDatetimeEqual(cls, json1['last_login'], user.last_login)
    if not(user.is_staff or user.is_superuser or int(user.id) == int(json1['id'])):
        cls.assertEqual(json1['username'], '***')
        cls.assertEqual(cls, json1['student_id'], user.userprofile.student_id[0:4])
    else:
        cls.assertEqual(json1['username'], user.username)
        cls.assertEqual(json1['student_id'], user.userprofile.student_id)


def assertActivityDetailEqual(cls: TestCase, content: Union[str, Dict], activity: Activity):
    """
    比较 REST API 返回的 Activity 和数据库中的 Activity 是否相同
    """
    compare_fields = set(ActivitySerializer.Meta.fields) - {'presenter', 'attender', 'datetime'}  # 时间正确性不能通过字符串比较

    if type(content) is dict:
        json1 = content
    else:
        json1 = json.loads(content)
    json2 = ActivitySerializer(activity).data
    for field in compare_fields:
        cls.assertEqual(json1[field], json2[field])  # 获取的数据和数据库中的数据在 json 意义上等价
    # 比较 datetime 是否正确
    assertDatetimeEqual(cls, json1['datetime'], activity.datetime)
    # 比较 presenter 是否正确
    presenter_data_response = set(map(lambda u: u['id'], json1['presenter']))
    presenter_data_db = set(map(lambda u: u.id, activity.presenter.all()))
    cls.assertEqual(presenter_data_response, presenter_data_db)
    # 比较 attender 是否正确
    attender_data_response = UserBriefSerializer(data=json1['attender'], many=True).initial_data
    attender_data_db = UserBriefSerializer(activity.attender.all(), many=True).data
    cls.assertEqual(attender_data_response, attender_data_db)
