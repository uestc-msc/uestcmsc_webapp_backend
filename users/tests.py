import json
from datetime import timedelta
from random import random, randrange
from typing import List, Dict

from django.test import TestCase, Client
from django.utils.timezone import now

from users.models import ResetPasswordRequest, UserProfile
from utils import generate_uuid
from utils.tester import *
from django.contrib.auth.models import User


# 注册相关测试
class SignUpTests(TestCase):
    def test_sign_up_with_empty_field(self):
        r = Client().post('/users/')
        self.assertEqual(r.status_code, 400)
        error_argument = set(eval(r.content).keys())
        self.assertEqual(error_argument, {'username', 'password', 'first_name', 'student_id'})

        r = tester_signup('admin@example.com', 'adminadmin', '', '123456')
        self.assertEqual(r.status_code, 400)
        error_argument = set(eval(r.content).keys())
        self.assertEqual(error_argument, {'first_name'})

        r = tester_signup('admin@example.com', '', 'ad', '123456')
        self.assertEqual(r.status_code, 400)
        error_argument = set(eval(r.content).keys())
        self.assertEqual(error_argument, {'password'})

        r = tester_signup('', 'adminadmin', 'ad', '123456')
        self.assertEqual(r.status_code, 400)
        error_argument = set(eval(r.content).keys())
        self.assertEqual(error_argument, {'username'})

        r = tester_signup('admin@example.com', 'adminadmin', 'ad', '')
        self.assertEqual(r.status_code, 400)
        error_argument = set(eval(r.content).keys())
        self.assertEqual(error_argument, {'student_id'})

    def test_sign_up_with_invalid_field(self):
        r = tester_signup('admin@example.com', 'adminadmin', 'ad', '123456')
        self.assertEqual(r.status_code, 201)

        r = tester_signup('admin1@example.com', 'adminadmin', 'ad', '123456')
        self.assertEqual(r.status_code, 400)
        error_argument = set(eval(r.content).keys())
        self.assertEqual(error_argument, {'student_id'})

        r = tester_signup('admin5@example.com', 'adminadmin', 'ad', '3e5')
        self.assertEqual(r.status_code, 400)
        error_argument = set(eval(r.content).keys())
        self.assertEqual(error_argument, {'student_id'})

        r = tester_signup('admin3@example.com', 'admina', 'ad', '1234567')
        self.assertEqual(r.status_code, 201)

        r = tester_signup('admin4@example.com', 'admin', 'ad', '12345678')
        self.assertEqual(r.status_code, 400)
        error_argument = set(eval(r.content).keys())
        self.assertEqual(error_argument, {'password'})

        r = tester_signup('admin@example.com', 'adminadmin', 'ad', '12345678')
        self.assertEqual(r.status_code, 400)
        error_argument = set(eval(r.content).keys())
        self.assertEqual(error_argument, {'username'})

        r = tester_signup('admin6@example.com', 'adminadmin', 'ad', '1234567890')
        self.assertEqual(r.status_code, 201)

        r = tester_signup('uestcmsc@outlook.com', 'passw0rd', '电子科技大学微软学生俱乐部', '20201024')
        self.assertEqual(r.status_code, 201)

        r = tester_signup('admin', 'adminadmin', 'Admin', '1234567890123456')
        self.assertEqual(r.status_code, 400)
        error_argument = set(eval(r.content).keys())
        self.assertEqual(error_argument, {'username'})


class UserListTest(TestCase):
    user_list_url = '/users/'

    def check_order(self, results: List[Dict]):
        """
        检查 results 是否是按经验降序排列的
        """
        exp = list(map(lambda u: int(u["experience"]), results))
        self.assertEqual(sorted(exp, reverse=True), exp)

    def setUp(self):
        tester_signup()

    def test_get_user_list(self):
        tester_signup('account@example.com', 'qwerty', 'account', '1234567')
        u = User.objects.filter(username='account@example.com')[0]
        u.userprofile.experience = 1
        u.userprofile.save()
        tester_signup('account1@example.com', 'qwerty', 'account1', '12345678')
        u = User(username="user@example.com", first_name="user")
        up = UserProfile(user=u, student_id='233', about="你好，世界！", experience="5")
        u.save()
        up.save()
        self.assertEqual(User.objects.count(), 4)

        c = Client()
        r = c.get(self.user_list_url)
        self.assertEqual(r.status_code, 401)

        tester_login(client=c)
        r = c.get(self.user_list_url)
        self.assertEqual(r.status_code, 200)
        import json
        json_content = json.loads(r.content)
        results = json_content['results']
        self.assertEqual(['5', '1', '0', '0'], list(map(lambda u: u['experience'], results))) # 可见结果经过排序

    def test_search_user(self):
        def check_search_queryset(results: List[Dict], keywords: str):
            self.check_order(results)
            results_pk = map(lambda u: str(u['pk']), results)
            for u in User.objects.all(): # 检查 user 是否应当出现在搜索结果中
                self.assertEqual(str(u.pk) in results_pk,
                                 keywords in (u.username + u.first_name + u.userprofile.student_id),
                                 "keywords: %s\t"
                                 "username: %s\t"
                                 "first_name: %s\t"
                                 "student_id: %s" % (keywords, u.username, u.first_name, u.userprofile.student_id))

        for i in range(1, 40):
            u = User(username="user%d@example.com" % i, first_name="user%d" % (i+78))
            up = UserProfile(user=u, student_id=str(i + 55), about="你好，世界！", experience=randrange(1, 1000))
            u.save()
            up.save()
        self.assertEqual(User.objects.count(), 40)

        c = Client()
        tester_login(client=c)
        test_keywords = list('1234567890') + ['hello', 'user', '1@example', '@']
        for keyword in test_keywords:
            r = c.get("%s?keyword=%s&page_size=100" % (self.user_list_url, keyword))
            self.assertEqual(r.status_code, 200)
            json_content = json.loads(r.content)
            results = json_content['results']
            check_search_queryset(results, keyword)


    def test_pagination(self):
        for i in range(1, 40):
            u = User(username="user%d@example.com" % i, first_name="user")
            up = UserProfile(user=u, student_id=str(i), about="你好，世界！", experience=str(i + 55))
            u.save()
            up.save()
        self.assertEqual(User.objects.count(), 40)

        c = Client()
        tester_login(client=c)

    def test_search_and_pagination(self):
        for i in range(1, 40):
            u = User(username="user%d@example.com" % i, first_name="user")
            up = UserProfile(user=u, student_id=str(i), about="你好，世界！", experience=str(i+55))
            u.save()
            up.save()
        self.assertEqual(User.objects.count(), 40)

        c = Client()
        tester_login(client=c)
        # r = c.get(self.user_list_url '?keyword=')



