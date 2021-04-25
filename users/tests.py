import json
from math import ceil
from random import randrange
from typing import List, Dict

from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase, Client
from django.urls import reverse
from django.utils.timezone import now

from users.models import UserProfile
from utils import Pagination
from utils.tester import tester_signup, tester_login, UserTestCase

user_list_url = reverse('user_list')
user_detail_url = lambda user_id: reverse('user_detail', args=[user_id])
change_password_url = lambda user_id: reverse('change_password', args=[user_id])
whoami_url = reverse('users_whoami')


class UserListTest(TestCase):
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
        user = User.objects.filter(username='account@example.com')[0]
        user.userprofile.experience = 1
        user.userprofile.save()
        tester_signup('account1@example.com', 'qwerty', 'account1', '12345678')
        user = User.objects.create(username="user@example.com", first_name="user")
        UserProfile.objects.create(user=user, student_id='233', about="你好，世界！", experience="5")
        self.assertEqual(User.objects.count(), 4)

        client = Client()
        response = client.get(user_list_url)
        self.assertEqual(response.status_code, 200)  # 未登录，get 返回 200

        tester_login(client=client)
        response = client.get(user_list_url)
        self.assertEqual(response.status_code, 200)
        json_content = response.json()
        results = json_content['results']
        self.check_order(results)
        self.assertEqual([5, 1, 0, 0], list(map(lambda u: u['experience'], results)))  # 可见结果经过排序

    def test_search(self):
        # 定义验证返回结果的函数
        def check_search_queryset(_results: List[Dict], keywords: str):
            self.check_order(_results)
            results_id = list(map(lambda _u: str(_u['id']), _results))
            for u in User.objects.all():  # 检查 user 是否应当出现在搜索结果中，结果是否和预期相同
                self.assertEqual(str(u.id) in results_id,
                                 keywords in (u.username + u.first_name + u.userprofile.student_id),
                                 "keywords=%s\t"
                                 "username=%s\t"
                                 "first_name=%s\t"
                                 "student_id=%s" % (keywords, u.username, u.first_name, u.userprofile.student_id))

        for i in range(1, 40):
            user = User.objects.create(username="user%d@example.com" % i, first_name="user%d" % (i + 78))
            UserProfile.objects.create(user=user, student_id=str(i + 55), about="你好，世界！", experience=randrange(1, 1000))
        self.assertEqual(User.objects.count(), 40)

        client = Client()
        tester_login(client=client)
        test_keywords = list('1234567890') + ['hello', 'user', '1@example', '@', '12', '23']  # 测试的关键字
        for keyword in test_keywords:
            response = client.get("%s?search=%s&page_size=100" % (user_list_url, keyword))  # page_size = 0 表示不分页
            self.assertEqual(response.status_code, 200)
            json_content = response.json()
            results = json_content['results']
            check_search_queryset(results, keyword)

        r1 = client.get("%s?search=&page_size=100" % user_list_url)
        r2 = client.get("%s?page_size=100" % user_list_url)
        self.assertEqual(json.loads(r1.content), json.loads(r2.content))  # search=<null> 应当不进行搜索

        r1 = client.get("%s?search=qwertyuiop&page_size=100" % user_list_url)
        self.assertEqual(r1.status_code, 200)  # 搜索无结果，返回 200
        self.assertEqual(json.loads(r1.content)["results"], [])  # 搜索无结果，返回 results=[]

    def test_pagination(self):
        total_users = 56
        for i in range(1, total_users):
            user = User.objects.create(username="user%d@example.com" % i, first_name="user")
            UserProfile.objects.create(user=user, student_id=str(i), experience=randrange(0, 1000))
        self.assertEqual(User.objects.count(), total_users)

        client = Client()
        tester_login(client=client)
        for page_size in [1, 2, 3, 5, 8, 13, 21, 34]:  # 计算这样分页的总页数和页大小
            total_pages = ceil(total_users / page_size)
            for page in range(1, total_pages):
                r1 = client.get("%s?search=&page_size=%s&page=%s" % (user_list_url, page_size, page))
                results1 = json.loads(r1.content)['results']
                count = json.loads(r1.content)['count']
                self.assertEqual(len(results1), page_size)  # 页大小正确
                self.assertEqual(count, total_users)  # 页数正确
                self.check_order(results1)  # 结果顺序正确
                r2 = client.get("%s?page=%s&page_size=%s" % (user_list_url, page, page_size))
                results2 = json.loads(r2.content)['results']
                self.assertEqual(results1, results2)  # 请求参数顺序不同，但结果相同
                # 判定 page_size 不合法时结果是否和默认 page_size 相同
                if page_size == Pagination.page_size:
                    for invalid_page_size in [-1, total_users, 0, 'qwerty']:
                        r3 = client.get("%s?&page_size=%s&" % (user_list_url, invalid_page_size))
                        self.assertEqual(r1.status_code, 200)
                        self.assertEqual(json.loads(r1.content), json.loads(r3.content))
            # 判定最后一页的正确性
            r1 = client.get("%s?&page_size=%s&=%s" % (user_list_url, page_size, total_pages))
            results1 = json.loads(r1.content)['results']
            self.assertEqual(len(results1), page_size)  # 页大小正确
            self.check_order(results1)  # 结果顺序正确
            # 判定 page 不合法时结果的正确性
            for page in [-1, total_pages + 1, 0, 'qwerty']:
                r1 = client.get("%s?&page_size=%s&page=%s" % (user_list_url, page_size, page))
                self.assertEqual(r1.status_code, 404, f"page={page}, page_size={page_size}")

    def test_user_privacy_protect(self):
        pass


class UserDetailTest(UserTestCase):
    def setUp(self):
        tester_signup("admin@example.com", "adminadmin", 'admin', "20210101", )
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
        client = Client()
        first_id = User.objects.first().id
        response = client.get(user_detail_url(first_id))
        self.assertEqual(response.status_code, 200)  # 未登录用户访问，返回 200

        tester_login(client=client)
        for u in User.objects.all():
            response = client.get(user_detail_url(u.id))
            self.assertUserDetailEqual(response.content, u)

    # 只测试 patch
    def test_patch_unauthorized(self):
        # 设置用户的权限
        superuser = User.objects.get(first_name="superuser")
        admin = User.objects.get(first_name="admin")
        modify_user = User.objects.get(first_name="user")
        another_user = User.objects.get(first_name="another_user")

        user_permissions = [  # 以五种用户身份去遍历
            [AnonymousUser, False],
            [superuser, True],
            [admin, True],
            [modify_user, True],
            [another_user, False]
        ]
        for user, permission in user_permissions:
            modify_user = User.objects.get(first_name="user")
            new_value = modify_user.last_name + '1'
            client = Client()
            if user != AnonymousUser:
                client.force_login(user)

            response = client.patch(user_detail_url(modify_user.pk),
                                    data={"last_name": new_value},
                                    content_type='application/json')
            self.assertEqual(response.status_code == 200, permission,
                             f"user={user}, status_code={response.status_code}")
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
        client = Client()
        client.force_login(user)
        for field, example in readonly_field_and_example.items():
            response = client.patch(user_detail_url(user.id),
                                    data={field: example},
                                    content_type='application/json')
            self.assertEqual(response.status_code, 200)
            response = client.get(user_detail_url(user.id))
            json_response = response.json()
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
        client = Client()
        client.force_login(u)
        response = client.get(user_detail_url(id))
        last_json = response.json()

        for field, example in field_and_example.items():
            response = client.patch(user_detail_url(id),
                                    data={field: example},
                                    content_type='application/json')
            self.assertEqual(response.status_code, 200)
            response = client.get(user_detail_url(id))
            current_json = response.json()

            last_json[field] = example
            self.assertEqual(current_json, last_json)  # 比较更新后 JSON 和预期 JSON

    def test_patch_with_invalid_value(self):
        field_and_wrong_example = [
            ["first_name", ""],
            ["student_id", ""],
            ["subscribe_email", "I don't want to"]
        ]
        user = User.objects.get(first_name="user")
        user.userprofile.student_id = "23333"
        user.userprofile.about = "233"
        user.userprofile.subscribe_email = True
        user.userprofile.save()
        client = Client()
        client.force_login(user)
        for field, example in field_and_wrong_example:
            response = client.patch(user_detail_url(user.id),
                                    data={field: example},
                                    content_type='application/json')
            self.assertEqual(response.status_code, 400, field + example)
            response = client.get(user_detail_url(user.id))
            json_response = response.json()
            self.assertNotEqual(json_response[field], example)

    def test_patch_one_field_in_userprofile_does_not_affect_others(self):
        user_before = User.objects.get(first_name="user")
        user_before.userprofile.student_id = '2333'
        user_before.userprofile.save()
        client = Client()
        client.force_login(user_before)
        response = client.patch(user_detail_url(user_before.id),
                                data={'about': 'hahaha'},
                                content_type='application/json')
        self.assertEqual(response.status_code, 200)
        user_after = User.objects.get(first_name="user")
        self.assertEqual(user_after.userprofile.student_id, '2333')
        self.assertEqual(user_after.userprofile.about, 'hahaha')

    def test_get_patch_user_with_no_userprofile(self):
        u = User(id=23333)
        u.save()
        self.assertEqual(hasattr(u, 'userprofile'), False)

        client = Client()
        tester_login(client=client)
        response = client.get(user_detail_url(23333))
        self.assertEqual(response.status_code, 200)  # 能够正确访问

        response = client.patch(user_detail_url(23333),
                                data={"about": "I'm 23333"},
                                content_type='application/json')
        self.assertEqual(response.status_code, 200)

        u = User.objects.get(id=23333)
        self.assertEqual(hasattr(u, 'userprofile'), True)  # Patch 操作创建了 userProfile
        self.assertEqual(u.userprofile.about, "I'm 23333")


class WhoAmITest(TestCase):
    def setUp(self):
        tester_signup()
        tester_signup("superuser@example.com", "supersuper", "superuser", "1297391")
        tester_signup("user@example.com", "useruser", "user", "1297392")
        tester_signup("anotheruser@example.com", "anotheruser", "anotheruser", "1297393")
        self.admin = User.objects.filter(first_name="admin")[0]

    def test_get_whoami(self):
        c = Client()
        tester_login(client=c)
        r1 = c.get(whoami_url)
        self.assertEqual(r1.status_code, 200)
        r2 = c.get(user_detail_url(self.admin.id))
        self.assertEqual(r1.content, r2.content)

    def test_get_unauthorized(self):
        r = Client().get(whoami_url)
        self.assertEqual(r.status_code, 401)


# 更改密码相关测试
class ChangePasswordTest(TestCase):
    email = "admin@example.com"
    password = "adminadmin"

    def setUp(self):
        tester_signup(self.email, self.password, 'Admin', '20210101')
        self.user = User.objects.filter(username=self.email).first()

    def test_change_password(self):
        c1 = Client()
        response = tester_login(self.email, self.password, c1)
        self.assertEqual(response.wsgi_request.user, self.user)
        response = c1.get('/')
        self.assertEqual(response.wsgi_request.user, self.user)

        c2 = Client()
        tester_login(self.email, self.password, c2)
        r2 = c2.patch(change_password_url(self.user.id),
                      {"old_password": self.password,
                       "new_password": "ADMINADMIN"},
                      content_type='application/json')

        self.assertEqual(r2.status_code, 204)
        response = c1.get('/')
        self.assertEqual(response.wsgi_request.user.is_authenticated, False)  # 此时第一个 Client 理应被下线
        response = c2.get('/')
        self.assertEqual(response.wsgi_request.user.is_authenticated, False)  # 此时第二个 Client 理应被下线

        response = tester_login(self.email, self.password, c1)
        self.assertEqual(response.status_code, 401)  # 尝试用旧密码登录
        response = tester_login(self.email, 'ADMINADMIN', c1)
        self.assertEqual(response.status_code, 200)  # 尝试用新密码登录
        r2 = tester_login(self.email, self.password, c2)
        self.assertEqual(r2.status_code, 401)  # 尝试用旧密码登录

        response = c1.patch(change_password_url(self.user.id),
                            {"old_password": "ADMINADMIN",
                             "new_password": self.password},
                            content_type='application/json')
        self.assertEqual(response.status_code, 204)  # 将密码改回来
        response = tester_login(self.email, self.password, c1)
        self.assertEqual(response.status_code, 200)

    def test_change_email_and_password(self):
        c1 = Client()
        response = tester_login(self.email, self.password, c1)
        self.assertEqual(response.wsgi_request.user, self.user)
        response = c1.patch(change_password_url(self.user.id),
                            {"old_password": self.password,
                             "new_password": "ADMINADMIN",
                             "new_email": "qwerty@example.com"},
                            content_type='application/json')
        self.assertEqual(response.status_code, 204)

        response = tester_login(self.email, self.password)
        self.assertEqual(response.status_code, 401)  # 旧账号无法登陆

        response = tester_login("qwerty@example.com", "ADMINADMIN")
        self.assertEqual(response.status_code, 200)  # 新账号可以登陆

    def test_change_password_with_invalid_field(self):
        tester_signup("another@example.com", "anotheruser", "another", "20201231")
        # 没上线
        client = Client()
        another_client = Client()
        response = client.patch(change_password_url(self.user.id),
                                {"old_password": self.password,
                                 "new_password": "ADMINADMIN"},
                                content_type='application/json')
        self.assertEqual(response.status_code, 401)
        response = tester_login("another@example.com", "anotheruser", another_client)
        self.assertEqual(response.status_code, 200)
        # 少密码字段
        response = tester_login(self.email, self.password, client)
        self.assertEqual(response.status_code, 200)
        response = client.patch(change_password_url(self.user.id),
                                {"new_password": "ADMINADMIN"},
                                content_type='application/json')
        self.assertEqual(response.status_code, 403)
        response = client.patch(change_password_url(self.user.id),
                                {"password": "anotheruser",
                                 "new_password": "ADMINADMIN"},
                                content_type='application/json')
        self.assertEqual(response.status_code, 403)
        # 旧密码错误
        response = client.patch(change_password_url(self.user.id),
                                {"old_password": "password",
                                 "new_email": 'test@example.com',
                                 "new_password": "ADMINADMIN", },
                                content_type='application/json')
        self.assertEqual(response.status_code, 403)
        response = tester_login("another@example.com", "anotheruser", another_client)
        self.assertEqual(response.status_code, 200)  # 邮箱没有被修改
        # 新密码强度不够
        response = client.patch(change_password_url(self.user.id),
                                {"old_password": self.password,
                                 "new_password": "other"},
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)
        # 邮箱不合法
        response = client.patch(change_password_url(self.user.id),
                                {"old_password": self.password,
                                 "new_email": "qwerty"},
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)
        # 邮箱已被占用
        response = client.patch(change_password_url(self.user.id),
                                {"old_password": self.password,
                                 "new_email": 'another@example.com'},
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response = tester_login("another@example.com", "anotheruser", another_client)
        self.assertEqual(response.status_code, 200)  # 密码没有被修改

    # TODO: 管理员修改普通用户/管理员/超级用户的信息、超级用户修改其他用户的信息
    def admin_change_email_and_password(self):
        pass
