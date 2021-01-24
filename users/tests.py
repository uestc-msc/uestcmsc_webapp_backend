import json
from math import ceil
from random import randrange
from typing import List, Dict

from django.contrib.auth.models import User, AnonymousUser
from django.test import TestCase
from django.utils.timezone import now

from users.models import UserProfile
from users.serializer import UserSerializer
from utils import MyPagination
from utils.tester import *


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
        self.assertEqual(r.status_code, 403)  # 未登录，get 返回 403

        tester_login(client=c)
        r = c.get(self.user_list_url)
        self.assertEqual(r.status_code, 200)
        import json
        json_content = json.loads(r.content)
        results = json_content['results']
        self.check_order(results)
        self.assertEqual([5, 1, 0, 0], list(map(lambda u: u['experience'], results)))  # 可见结果经过排序

    def test_search(self):
        def check_search_queryset(_results: List[Dict], keywords: str):
            self.check_order(_results)
            results_id = list(map(lambda u: str(u['id']), _results))
            for u in User.objects.all():  # 检查 user 是否应当出现在搜索结果中，结果是否和预期相同
                self.assertEqual(str(u.id) in results_id,
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
        test_keywords = list('1234567890') + ['hello', 'user', '1@example', '@', '12', '23']    # 测试的关键字
        for keyword in test_keywords:
            r = c.get("%s?search=%s&page_size=100" % (self.user_list_url, keyword))   # page_size = 0 表示不分页
            self.assertEqual(r.status_code, 200)
            json_content = json.loads(r.content)
            results = json_content['results']
            check_search_queryset(results, keyword)

        r1 = c.get("%s?search=&page_size=100" % self.user_list_url)
        r2 = c.get("%s?page_size=100" % self.user_list_url)
        self.assertEqual(json.loads(r1.content), json.loads(r2.content))            # search=<null> 应当不进行搜索

        r1 = c.get("%s?search=qwertyuiop&page_size=100" % self.user_list_url)
        self.assertEqual(r1.status_code, 200)                                       # 搜索无结果，返回 200
        self.assertEqual(json.loads(r1.content)["results"], [])                     # 搜索无结果，返回 results=[]

    def test_pagination(self):
        total_users = 56
        for i in range(1, total_users):
            u = User(username="user%d@example.com" % i, first_name="user")
            up = UserProfile(user=u, student_id=str(i), experience=randrange(0, 1000))
            u.save()
            up.save()
        self.assertEqual(User.objects.count(), total_users)

        c = Client()
        tester_login(client=c)
        for page_size in [1, 2, 3, 5, 8, 13, 21, 34]:  # 计算这样分页的总页数和页大小
            total_pages = ceil(total_users / page_size)
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
                        self.assertEqual(json.loads(r1.content), json.loads(r3.content))
            # 判定最后一页的正确性
            r1 = c.get("%s?&page_size=%s&=%s" % (self.user_list_url, page_size, total_pages))
            results1 = json.loads(r1.content)['results']
            self.assertEqual(len(results1), page_size)              # 页大小正确
            self.check_order(results1)                              # 结果顺序正确
            # 判定 page 不合法时结果的正确性
            for page in [-1, total_pages+1, 0, 'qwerty']:
                r1 = c.get("%s?&page_size=%s&page=%s" % (self.user_list_url, page_size, page))
                self.assertEqual(r1.status_code, 404,  f"page={page}, page_size={page_size}")


class UserDetailTest(TestCase):
    def user_detail_url(self, id: int):
        return f'/users/{id}/'

    def compare_user_detail_json(self, content: str, user: User):
        compare_fields = set(UserSerializer.Meta.fields) - {'last_login', 'date_joined'}   # 不比较时间类的正确性
        json1 = json.loads(content)
        json2 = UserSerializer(user).data
        for field in compare_fields:
            self.assertEqual(json1[field], json2[field])  # 获取的数据和数据库中的数据在 json 意义上等价
        self.assertEqual('last_login' in json1, True)
        self.assertEqual('date_joined' in json1, True)

    def setUp(self):
        tester_signup("admin@example.com", "adminadmin", 'admin', "20210101",)
        u = User.objects.get(first_name='admin')
        u.is_staff = True
        u.save()
        tester_signup('superuser@example.com', 'qwerty', 'superuser', '1234567')
        u = User.objects.get(first_name='superuser')
        u.userprofile.experience = 1
        u.is_superuser = True
        u.userprofile.save()
        u.save()
        tester_signup('user@example.com', 'qwerty', 'user', '12345679')
        u = User(username="another_user@example.com",
                 first_name="another_user",
                 last_name="clever",
                 last_login=now(),
                 date_joined=now())
        up = UserProfile(user=u,
                         student_id='233',
                         about="你好，世界！",
                         experience=5)
        u.save()
        up.save()
        self.assertEqual(User.objects.count(), 4)

    def test_get(self):
        c = Client()
        first_id = User.objects.first().id
        r = c.get(self.user_detail_url(first_id))
        self.assertEqual(r.status_code, 403)  # 未登录用户访问

        tester_login(client=c)
        for u in User.objects.all():
            r = c.get(self.user_detail_url(u.id))
            self.compare_user_detail_json(r.content, u)

    # 只测试 patch
    def test_patch_unauthorized(self):
        # 设置用户的权限
        superuser = User.objects.get(first_name="superuser")
        admin = User.objects.get(first_name="admin")
        modify_user = User.objects.get(first_name="user")
        another_user = User.objects.get(first_name="another_user")

        user_permissions = [ # 以五种用户身份去遍历
            [AnonymousUser, False],
            [superuser, True],
            [admin, True],
            [modify_user, True],
            [another_user, False]
        ]
        for user, permission in user_permissions:
            modify_user = User.objects.get(first_name="user")
            new_value = modify_user.last_name + '1'
            c = Client()
            if user != AnonymousUser:
                c.force_login(user)

            r = c.patch(self.user_detail_url(modify_user.pk),
                        data={"last_name": new_value},
                        content_type='application/json')
            self.assertEqual(r.status_code == 200, permission,
                             f"user={user}, status_code={r.status_code}")
            modify_user = User.objects.get(first_name="user")
            self.assertEqual(new_value == modify_user.last_name, permission,
                             f"user={user}, new_value={new_value}, current={modify_user.last_name}")

    def test_patch_readonly_field(self):
        readonly_field_and_example = {
            "id": 233,
            "username": "hello@example.com",
            "experience": 233,
            "avatar_url": "https://uestc-msc.github.io/",
            "last_login": now(),
            "date_joined": now(),
            "is_staff": True,
            "is_superuser": True
        }
        user = User.objects.get(first_name="user")
        c = Client()
        c.force_login(user)
        for field, example in readonly_field_and_example.items():
            r = c.patch(self.user_detail_url(user.id),
                        data={field: example},
                        content_type='application/json')
            self.assertEqual(r.status_code, 200)
            modify_user = User.objects.get(first_name="user")
            r = c.get(self.user_detail_url(user.id))
            json_response = json.loads(r.content)
            self.assertNotEqual(json_response[field], example)

    def test_patch_correctly(self):
        field_and_example = {
            "first_name": "string",
            "last_name": "string",
            "student_id": "4231423",
            "about": "hello everyone!",
            "subscribe_email": True
        }
        u = User.objects.get(first_name="user")
        id = u.id
        c = Client()
        c.force_login(u)
        for field, example in field_and_example.items():
            r = c.patch(self.user_detail_url(id),
                        data={field: example},
                        content_type='application/json')
            self.assertEqual(r.status_code, 200)
            modify_user = User.objects.get(id=id)
            r = c.get(self.user_detail_url(id))
            json_response = json.loads(r.content)
            self.assertEqual(json_response[field], example)

    def test_patch_with_invalid_value(self):
        field_and_wrong_example = {
            "first_name": "",
            "student_id": "",
            "about": "",
            "subscribe_email": "I don't want to"
        }
        user = User.objects.get(first_name="user")
        user.userprofile.student_id = "23333"
        user.userprofile.about = "233"
        user.userprofile.subscribe_email = True
        user.userprofile.save()
        c = Client()
        c.force_login(user)
        for field, example in field_and_wrong_example.items():
            r = c.patch(self.user_detail_url(user.id),
                        data={field: example},
                        content_type='application/json')
            self.assertEqual(r.status_code, 400, field + example)
            modify_user = User.objects.get(first_name="user")
            r = c.get(self.user_detail_url(user.id))
            json_response = json.loads(r.content)
            self.assertNotEqual(json_response[field], example)

    def test_patch_one_field_in_userprofile_does_not_affect_others(self):
        user_before = User.objects.get(first_name="user")
        user_before.userprofile.student_id = '2333'
        user_before.userprofile.save()
        c = Client()
        c.force_login(user_before)
        r = c.patch(self.user_detail_url(user_before.id),
                data={'about': 'hahaha'},
                content_type='application/json')
        self.assertEqual(r.status_code, 200)
        user_after = User.objects.get(first_name="user")
        self.assertEqual(user_after.userprofile.student_id, '2333')
        self.assertEqual(user_after.userprofile.about, 'hahaha')

    def test_get_patch_user_with_no_userprofile(self):
        u = User(id=23333)
        u.save()
        self.assertEqual(hasattr(u, 'userprofile'), False)

        c = Client()
        tester_login(client=c)
        r = c.get(self.user_detail_url(23333))
        self.assertEqual(r.status_code, 200) # 能够正确访问

        r = c.patch(self.user_detail_url(23333),
                    data={"about":"I'm 23333"},
                    content_type='application/json')
        self.assertEqual(r.status_code, 200)

        u = User.objects.get(id=23333)
        self.assertEqual(hasattr(u, 'userprofile'), True) # Patch 操作创建了 userProfile
        self.assertEqual(u.userprofile.about, "I'm 23333")