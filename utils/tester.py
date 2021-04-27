import json
from datetime import datetime, timedelta
from os import path
from typing import Union, List, Dict
from unittest.case import skipIf

import requests
from django.contrib.auth.models import User
from django.test import Client, SimpleTestCase, TestCase
from django.urls import reverse

from activities.models import Activity
from activities.serializer import ActivitySerializer
from cloud.onedrive import *
from cloud.onedrive.api.cache import get_access_token, get_refresh_token, set_access_token, set_refresh_token
from uestcmsc_webapp_backend.settings import APP_NAME
from users.serializer import UserBriefSerializer, UserSerializer


########################################


# 测试时用于创建一个默认账户。也可以用于给定参数创建账户
def tester_signup(username: str = "admin@example.com", password: str = "adminadmin", first_name: str = 'admin',
                  student_id: str = "20210101", client: Client = None):
    if client is None:
        client = Client()
    from accounts.tests import signup_url
    return client.post(signup_url, {'username': username, 'password': password,
                                    'first_name': first_name, 'student_id': student_id})


# 测试时用于登录一个默认账户。也可以用于给定参数登录指定账户
def tester_login(username: str = 'admin@example.com', password: str = "adminadmin",
                 client: Client = None):
    if client is None:
        client = Client()
    from accounts.tests import login_url
    return client.post(login_url, {'username': username, 'password': password})


# 测试时用于创建一个默认活动。也可以用于给定参数创建活动
def tester_create_activity(title: str = "测试沙龙", date_time: Union[str, datetime] = "2021-01-01T08:00:00.000+08:00",
                           location: str = "GitHub", presenter_ids: List[int] = None, client: Client = None):
    if client is None:
        client = Client()
        tester_signup(client=client)
        tester_login(client=client)
    if presenter_ids is None:
        presenter_ids = [User.objects.first().id]
    presenter = list(map(lambda id: {"id": id}, presenter_ids))
    url = reverse('activity_list')
    data = {'title': title, 'datetime': date_time, 'location': location, 'presenter': presenter}
    return client.post(url, data, content_type='application/json')


########################################


class TimeTestCase(SimpleTestCase):
    # 比较两个时间是否在误差 1s 内相等（因为 Django 模型的 datetime 只精确到 1ms）
    def assertDatetimeEqual(self, dt1: Union[datetime, str], dt2: datetime):
        if dt1 is None:
            return dt2 is None
        if type(dt1) is str:
            dt1 = datetime.fromisoformat(dt1)
        self.assertLess(abs(dt1 - dt2), timedelta(seconds=1), f"{dt1}!={dt2}")


########################################


class UserTestCase(TestCase, TimeTestCase):
    # 比较 REST API 返回的 User 和数据库中 User 是否相同
    def assertUserDetailEqual(self, content: str, user: User):
        # 时间正确性不能通过字符串比较
        compare_fields = set(UserSerializer.Meta.fields) - {'last_login', 'date_joined', 'username', 'student_id'}
        json1 = json.loads(content)
        json2 = UserSerializer(user).data
        for field in compare_fields:
            self.assertEqual(json1[field], json2[field])  # 获取的数据和数据库中的数据在 json 意义上等价
        self.assertDatetimeEqual(json1['date_joined'], user.date_joined)
        self.assertDatetimeEqual(json1['last_login'], user.last_login)
        if not (user.is_staff or user.is_superuser or int(user.id) == int(json1['id'])):
            self.assertEqual(json1['username'], '***')
            self.assertEqual(self, json1['student_id'], user.userprofile.student_id[0:4])
        else:
            self.assertEqual(json1['username'], user.username)
            self.assertEqual(json1['student_id'], user.userprofile.student_id)


class ActivityTestCase(TestCase, TimeTestCase):
    # 比较 REST API 返回的 Activity 和数据库中的 Activity 是否相同
    def assertActivityDetailEqual(self, content: Union[str, Dict], activity: Activity):
        # 时间正确性不能通过字符串比较
        compare_fields = set(ActivitySerializer.Meta.fields) - {'presenter', 'attender', 'datetime'}

        if type(content) is dict:
            json1 = content
        else:
            json1 = json.loads(content)
        json2 = ActivitySerializer(activity).data
        for field in compare_fields:
            self.assertEqual(json1[field], json2[field])  # 获取的数据和数据库中的数据在 json 意义上等价
        # 比较 datetime 是否正确
        self.assertDatetimeEqual(json1['datetime'], activity.datetime)
        # 比较 presenter 是否正确
        presenter_data_response = set(map(lambda u: u['id'], json1['presenter']))
        presenter_data_db = set(map(lambda u: u.id, activity.presenter.all()))
        self.assertEqual(presenter_data_response, presenter_data_db)
        # 比较 attender 是否正确
        attender_data_response = set(map(lambda u: u['id'], json1['attender']))
        attender_data_db = set(map(lambda u: u.id, activity.attender.all()))
        self.assertEqual(attender_data_response, attender_data_db)


# 在测试数据库中读不到数据，但是在测试前还是可以读到数据
# 所以在测试前把 refresh_token 读出来，就可以装进数据库了
_access_token = get_access_token()
_refresh_token = get_refresh_token()


# 所有 Onedrive 相关测试都应当将该类作为父类
@skipIf(_refresh_token is None, "Onedrive Not Login")
class OnedriveTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # 在测试数据库中设置 access_token 和 refresh_token
        set_access_token(_access_token)
        set_refresh_token(_refresh_token)
        # 替换测试路径为 /应用/{APP_NAME}_test
        onedrive_approot.uri = onedrive_drive.find_file_by_path(f'/应用/{APP_NAME}_test').uri
        onedrive_activity_directory.uri = onedrive_approot.find_file_by_path('沙龙').uri
        onedrive_temp_directory.uri = onedrive_approot.find_file_by_path('temp').uri
        # 创建应用 test 文件夹
        onedrive_root.create_directory_recursive(f'/应用/{APP_NAME}_test')

    @classmethod
    def tearDownClass(cls):
        onedrive_approot.delete()        # 删除应用 test 文件夹
        super().tearDownClass()

    # 使用本后端的文件上传 API 上传文件，上传完成后返回 id
    def upload_file(self, filepath: str = 'static/ruanweiwei.png', client: Client = None) -> str:
        if client is None:
            client = Client()
            tester_signup(client=client)
            tester_login(client=client)
        self.assertIs(path.isfile(filepath), True, f"{filepath} does not exists.")
        filename = filepath.split('/')[-1]
        # 创造上传会话
        from cloud.tests import onedrive_file_url
        response = client.post(onedrive_file_url, {"filename": filename})
        self.assertEqual(response.status_code, 200)
        content = eval(response.content)
        if type(content) is str:    # 有时候是 dict 有时候是 str 我也不知道为什么会这样
            content = eval(content)
        else:
            print('content is dict')
        self.assertEqual(type(content), dict)
        upload_url = content['uploadUrl']
        # 上传文件
        with open(filepath, 'rb') as file:
            file_data = file.read()
            file_length = len(file_data)
            self.assertLessEqual(file_length, 60 * (2 ** 20), "上传文件应当需要小于 60 MiB")
            headers = {"Content-Range": f"bytes 0-{file_length - 1}/{file_length}"}
            response = requests.put(upload_url, data=file_data, headers=headers)
            self.assertEqual(response.status_code, 201, f"上传错误，response.content 为：\n{response.json()}")
            return response.json()['id']
