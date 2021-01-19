import json
from datetime import timedelta
from random import random, randrange
from typing import List, Dict

from django.test import TestCase, Client
from django.utils.timezone import now

from users.models import ResetPasswordRequest, UserProfile
from users.serializer import UserSerializer
from utils import generate_uuid, MyPagination
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
        self.check_order(results)
        self.assertEqual([5, 1, 0, 0], list(map(lambda u: u['experience'], results))) # 可见结果经过排序

    def test_search(self):
        def check_search_queryset(results: List[Dict], keywords: str):
            self.check_order(results)
            results_pk = list(map(lambda u: str(u['pk']), results))
            for u in User.objects.all(): # 检查 user 是否应当出现在搜索结果中，结果是否和预期相同
                self.assertEqual(str(u.pk) in results_pk,
                                 keywords in (u.username + u.first_name + u.userprofile.student_id),
                                 "keywords=%s\t"
                                 "username=%s\t"
                                 "first_name=%s\t"
                                 "student_id=%s" % (keywords, u.username, u.first_name, u.userprofile.student_id))

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
            r = c.get("%s?search=%s&page_size=0" % (self.user_list_url, keyword))   # page_size = 0 表示不分页
            self.assertEqual(r.status_code, 200)
            json_content = json.loads(r.content)
            results = json_content['results']
            check_search_queryset(results, keyword)

        r1 = c.get("%s?search=&page_size=0" % self.user_list_url)
        r2 = c.get("%s&page_size=0" % self.user_list_url)
        self.assertEqual(json.loads(r1.content), json.loads(r2.content))            # search=<null> 应当不进行搜索

        r1 = c.get("%s?search=qwertyuiop&page_size=0" % self.user_list_url)
        self.assertEqual(r1.status_code, 200)                                       # 搜索无结果，返回 200
        self.assertEqual(json.loads(r1.content)["results"], [])                     # 搜索无结果，返回 results=[]

    def test_pagination(self):
        total_users = 56
        for i in range(1, total_users):
            u = User(username="user%d@example.com" % i, first_name="user")
            up = UserProfile(user=u, student_id=str(i), experience=randrange(0,1000))
            u.save()
            up.save()
        self.assertEqual(User.objects.count(), total_users)

        c = Client()
        tester_login(client=c)
        for page_size in range(1, total_users): # 计算这样分页的总页数和页大小
            last_page_size = total_users % page_size
            total_pages = total_users // page_size
            if last_page_size == 0:
                last_page_size = page_size
            else:
                total_pages += 1
            for page in range(1, total_pages):
                r1 = c.get("%s?search=&page_size=%s&page=%s" % (self.user_list_url, page_size, page))
                results1 = json.loads(r1.content)['results']
                count = json.loads(r1.content)['count']
                self.assertEqual(len(results1), page_size)          # 页大小正确
                self.assertEqual(count, total_users)                # 页数正确
                self.check_order(results1)                          # 结果顺序正确
                r2 = c.get("%s?page=%s&page_size=%s" % (self.user_list_url, page, page_size))
                results2 = json.loads(r2.content)['results']
                self.assertEqual(results1, results2)                # 请求参数顺序不同，但结果相同
                # 判定 page_size 不合法时结果是否和默认 page_size 相同
                if page_size == MyPagination.page_size:
                    for invalid_page_size in [-1, total_users, 0, 'qwerty']:
                        r3 = c.get("%s?&page_size=%s&" % (self.user_list_url, invalid_page_size))
                        self.assertEqual(r1.status_code, 200)
                        self.assertEqual(json.loads(r1.content),json.loads(r1.content))
            # 判定最后一页的正确性
            r1 = c.get("%s?&page_size=%s&=%s" % (self.user_list_url, page_size, total_pages))
            results1 = json.loads(r1.content)['results']
            self.assertEqual(len(results1), page_size)              # 页大小正确
            self.check_order(results1)                              # 结果顺序正确
            # 判定 page 不合法时结果的正确性
            for page in [-1, total_pages+1, 0, 'qwerty']:
                r1 = c.get("%s?&page_size=%s&page=%s" % (self.user_list_url, page_size, page))
                self.assertEqual(r1.status_code, 404,  f"page={page}, page_size={page_size}")


class UserProfileTest(TestCase):
    def user_profile_url(self, pk: int):
        return f'/users/{pk}/'

    def compare_json(self, content: str, user: User):
        compare_fields = ('pk', 'username', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'student_id', 'experience', 'experience', 'about', 'avatar_url')
        json1 = json.loads(content)
        json2 = UserSerializer(user).data
        for field in compare_fields:
            self.assertEqual(json1[field], json2[field])  # 获取的数据和数据库中的数据在 json 意义上等价

    def setUp(self):
        tester_signup()
        tester_signup('account@example.com', 'qwerty', 'account', '1234567')
        u = User.objects.filter(username='account@example.com')[0]
        u.userprofile.experience = 1
        u.userprofile.save()
        tester_signup('account1@example.com', 'qwerty', 'account1', '12345679')
        u = User(username="user@example.com", first_name="user")
        up = UserProfile(user=u, student_id='233', about="你好，世界！", experience="5")
        u.save()
        up.save()
        self.assertEqual(User.objects.count(), 4)

    def test_get(self):
        c = Client()
        first_pk = User.objects.first().pk
        r = c.get(self.user_profile_url(first_pk))
        self.assertEqual(r.status_code, 403) # 未登录用户访问

        tester_login(client=c)
        for u in User.objects.all():
            r = c.get(self.user_profile_url(u.pk))
            self.compare_json(r.content, u)

    def test_put_patch(self):
        for method in 'put', 'patch':
            c = Client()
            first_pk = User.objects.first().pk
            r = c.get(self.user_profile_url(first_pk))
            self.assertEqual(r.status_code, 403)  # 未登录用户访问

            tester_login(client=c)
            for u in User.objects.all():
                r = c.get(self.user_profile_url(u.pk))
                self.compare_json(r.content, u)




