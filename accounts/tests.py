from datetime import timedelta
from random import random

from django.test import TestCase, Client
from django.utils.timezone import now

from users.models import ResetPasswordRequest
from utils import generate_uuid
from utils.tester import *
from django.contrib.auth.models import User
# Create your tester here.


# 登录相关测试
class LoginTest(TestCase):
    def setUp(self):
        r = tester_signup('admin@example.com', 'adminadmin', 'Admin', '20210101')
        self.admin_user = User.objects.get(username='admin@example.com')
        tester_signup('user@example.com', 'useruser', 'User', '20210104')
        self.another_user = User.objects.get(username='user@example.com')

    def test_login_correctly(self):
        r = tester_login('admin@example.com', 'adminadmin')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.wsgi_request.user, self.admin_user)

        r = tester_login('admin@example.com', 'adminadmin')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.wsgi_request.user, self.admin_user)

    def test_login_with_less_argument(self):
        r = Client().post('/accounts/login/')
        self.assertEqual(r.status_code, 401)

        r = Client().post('/accounts/login/')
        self.assertEqual(r.status_code, 401)

        r = Client().get('/accounts/login/')
        self.assertEqual(r.status_code, 405)

        r = Client().post('/accounts/login/', {"username": "admin@example.com"})
        self.assertEqual(r.status_code, 401)

        r = Client().post('/accounts/login/', {"password": "adminadmin"})
        self.assertEqual(r.status_code, 401)

        r = tester_login('admin', '')
        self.assertEqual(r.status_code, 401)

        r = tester_login('', 'admin')
        self.assertEqual(r.status_code, 401)

    def test_login_with_invalid_authentication(self):
        r = tester_login('user@example.com', 'useruser')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.wsgi_request.user, self.another_user)

        r = tester_login('user@example.com', 'admin')
        self.assertEqual(r.status_code, 401)

        r = tester_login('admin@example.com', 'USERUSER')
        self.assertEqual(r.status_code, 401)

        r = tester_login('admin@example.com', 'adminadmin')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.wsgi_request.user, self.admin_user)

        r = tester_login('admin@example.com', 'admin')
        self.assertEqual(r.status_code, 401)

        r = tester_login('admin', 'adminadmin')
        self.assertEqual(r.status_code, 401)

        r = tester_login('admin@example.com', 'useruser')
        self.assertEqual(r.status_code, 401)

        r = tester_login('user@example.com', 'adminadmin')
        self.assertEqual(r.status_code, 401)

    def test_login_by_switch_user(self):
        c = Client()
        r = tester_login('admin@example.com', 'adminadmin', c)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.wsgi_request.user, self.admin_user)

        r = tester_login('user@example.com', 'useruser', c)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.wsgi_request.user, self.another_user)

        r = tester_login('wrong', 'wrongpassword', c)
        self.assertEqual(r.status_code, 401)

        r = tester_login('admin@example.com', 'adminadmin', c)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.wsgi_request.user, self.admin_user)


# 登出相关测试
class LogoutTest(TestCase):
    def test_log_out(self):
        tester_signup("admin@example.com", "adminadmin")
        r = Client().post('/accounts/logout/')
        self.assertEqual(r.status_code, 401)

        r = tester_login("admin@example.com", "adminadmin")
        self.assertEqual(r.wsgi_request.user, User.objects.first())
        r = r.client.post('/accounts/logout/')
        self.assertEqual(r.status_code, 204)
        self.assertEqual(r.wsgi_request.user.is_authenticated, False)


class ResetPasswordTest(TestCase):
    email = "admin@example.com"
    password = "adminadmin"

    def setUp(self):
        tester_signup(self.email, self.password, 'Admin', '20210101')
        self.user = User.objects.first()

    # Django test 中不会真的发送邮件
    # 文档：https://docs.djangoproject.com/zh-hans/3.1/topics/testing/tools/#email-services
    def test_forget_password_whole_process(self):
        c = Client()
        r = tester_login(self.email, self.password, c)
        self.assertEqual(r.wsgi_request.user, self.user)
        r = c.get('/')
        self.assertEqual(r.wsgi_request.user, self.user)

        c2 = Client()
        r = c2.post('/accounts/forget_password/', {"email": self.email})
        self.assertEqual(r.status_code, 202)

        token = pop_token_from_virtual_mailbox(self)
        r = c2.post('/accounts/reset_password/', {
            "token": token
        })
        self.assertEqual(r.status_code, 200)  # token 有效

        r = c2.post('/accounts/reset_password/', {
            "token": token,
            "new_password": "new_password"
        })
        self.assertEqual(r.status_code, 204)

        r = c.get('/')
        self.assertEqual(r.wsgi_request.user.is_authenticated, False)  # 此时第一个 Client 理应被下线
        r = c2.get('/')
        self.assertEqual(r.wsgi_request.user.is_authenticated, False)  # 此时第二个 Client 也应该不在线

        r = tester_login(self.email, self.password)
        self.assertEqual(r.status_code, 401)

        r = tester_login(self.email, 'new_password')
        self.assertEqual(r.status_code, 200)

        r = tester_login(self.email, self.password)
        self.assertEqual(r.status_code, 401)

    def test_forget_email_with_invalid_field(self):
        c = Client()
        r = tester_login(self.email, self.password, c)
        self.assertEqual(r.wsgi_request.user, self.user)

        r = c.post('/accounts/forget_password/', {"email": "12312313"})
        self.assertEqual(r.status_code, 400)
        r = c.post('/accounts/forget_password/', {"email": "Admin"})
        self.assertEqual(r.status_code, 400)
        r = c.post('/accounts/forget_password/', {"email": "example@example.com"})
        self.assertEqual(r.status_code, 400)
        r = c.post('/accounts/forget_password/', {"email": self.email})
        self.assertEqual(r.status_code, 202)

    def test_validate_token_with_invalid_field(self):
        tester_signup("another@example.com", "anotheruser", "another", "20201231")
        anotheruser = User.objects.filter(username="another@example.com").first()
        self.assertIsNotNone(anotheruser)
        c = Client()
        r = c.post('/accounts/forget_password/', {"email": self.email})
        self.assertEqual(r.status_code, 202)
        user_token = pop_token_from_virtual_mailbox(self)

        # 假 token
        r = c.post('/accounts/reset_password/', {
            "token": generate_uuid(),
            "new_password": "new_password"
        })
        self.assertEqual(r.status_code, 403)

        r = c.post('/accounts/reset_password/', {
            "token": generate_uuid()
        })
        self.assertEqual(r.status_code, 403)
        # 过期 token
        expired_token = generate_uuid()
        ResetPasswordRequest.objects.create(user=self.user, token=expired_token, request_time=now() - timedelta(days=2),
                                            ipv4addr="127.0.0.1")
        r = c.post('/accounts/reset_password/', {
            "token": expired_token
        })
        self.assertEqual(r.status_code, 403)
        # 弱密码
        r = c.post('/accounts/reset_password/', {
            "token": user_token,
            "new_password": "pd"
        })
        self.assertEqual(r.status_code, 400)
        self.assertEqual(eval(r.content)['message'], '新密码不合法')
        # 重复使用 token
        r = c.post('/accounts/reset_password/', {
            "token": user_token,
            "new_password": "new_password"
        })
        self.assertEqual(r.status_code, 204)
        r = c.post('/accounts/reset_password/', {
            "token": user_token,
            "new_password": "new_password"
        })
        self.assertEqual(r.status_code, 403)

    def test_forget_password_frequently(self):
        """
        封装成一个函数，对 1min 和 1day 分别调用
        先塞 n-1 封邮件，然后发两封，assert第一封成功第二封失败
        然后随便删掉一封，改为更远的时间，重新发两封，第一封成功第二封失败
        注意还要测删除的过程
        """
        tester_signup("another@example.com", "anotheruser", "another", "20201231")
        anotheruser = User.objects.filter(username="another@example.com").first()
        self.assertIsNotNone(anotheruser)

        testcases = [
            [timedelta(minutes=1), 1],
            [timedelta(days=1), 10]
        ]
        for tc in testcases:
            delta, number = tc
            for i in range(number - 1):  # 先塞 n-1 封邮件
                current_user = self.user if i % 2 else anotheruser  # 保证用户不同而 ip 相同
                ResetPasswordRequest.objects.create(user=current_user,
                                                    token=generate_uuid(),
                                                    request_time=now() - delta + timedelta(minutes=1),
                                                    ipv4addr='127.0.0.1')
            self.assertEqual(ResetPasswordRequest.objects.count(), number - 1)
            # 发两封，assert第一封成功第二封失败
            r = Client().post('/accounts/forget_password/', {"email": self.user.username})
            self.assertEqual(r.status_code, 202)
            r = Client().post('/accounts/forget_password/', {"email": self.user.username})
            self.assertEqual(r.status_code, 403)
            # 将最近一封改为更远的时间，重新发两封，第一封成功第二封失败
            rpr = ResetPasswordRequest.objects.order_by('request_time').last()
            rpr.request_time = now() - delta
            rpr.save()
            r = Client().post('/accounts/forget_password/', {"email": self.user.username})
            self.assertEqual(r.status_code, 202)
            self.assertEqual(ResetPasswordRequest.objects.filter(request_time__lt=now() - timedelta(days=1)).count(),
                             0)  # 保证过期的邮件有被清除
            r = Client().post('/accounts/forget_password/', {"email": self.user.username})
            self.assertEqual(r.status_code, 403)
            ResetPasswordRequest.objects.all().delete()


class ChangePasswordTest(TestCase):
    email = "admin@example.com"
    password = "adminadmin"

    def setUp(self):
        tester_signup(self.email, self.password, 'Admin', '20210101')
        self.user = User.objects.filter(username=self.email).first()
        self.password_url = '/accounts/change_password/'

    def test_reset_password(self):
        c1 = Client()
        r = tester_login(self.email, self.password, c1)
        self.assertEqual(r.wsgi_request.user, self.user)
        r = c1.get('/')
        self.assertEqual(r.wsgi_request.user, self.user)

        c2 = Client()
        tester_login(self.email, self.password, c2)
        r2 = c2.post(self.password_url, {"old_password": self.password, "new_password": "ADMINADMIN"})
        self.assertEqual(r2.status_code, 204)
        r = c1.get('/')
        self.assertEqual(r.wsgi_request.user.is_authenticated, False)  # 此时第一个 Client 理应被下线
        r = c2.get('/')
        self.assertEqual(r.wsgi_request.user.is_authenticated, False)  # 此时第二个 Client 理应被下线

        r = tester_login(self.email, self.password, c1)
        self.assertEqual(r.status_code, 401)
        r = tester_login(self.email, 'ADMINADMIN', c1)
        self.assertEqual(r.status_code, 200)
        r2 = tester_login(self.email, self.password, c2)
        self.assertEqual(r2.status_code, 401)

        r = c1.post(self.password_url, {"old_password": "ADMINADMIN", "new_password": self.password})
        self.assertEqual(r.status_code, 204)
        r = tester_login(self.email, self.password, c1)
        self.assertEqual(r.status_code, 200)

    def test_reset_password_with_invalid_field(self):
        tester_signup("another@example.com", "anotheruser", "another", "20201231")
        anotheruser = User.objects.filter(username="another@example.com").first()
        # 没上线
        c = Client()
        r = c.post(self.password_url, {"old_password": self.password, "new_password": "ADMINADMIN"})
        self.assertEqual(r.status_code, 401)
        r = tester_login("another@example.com", "anotheruser", c)
        self.assertEqual(r.status_code, 200)
        # 少字段
        r = tester_login(self.email, self.password, c)
        r = c.post(self.password_url, {"new_password": "ADMINADMIN"})
        self.assertEqual(r.status_code, 400)
        r = c.post(self.password_url, {"old_password": self.password})
        self.assertEqual(r.status_code, 400)
        r = c.post(self.password_url, {"old_password": self.password, "password": "ADMINADMIN"})
        self.assertEqual(r.status_code, 400)
        # 旧密码错误
        r = c.post(self.password_url, {"old_password": "password", "new_password": "ADMINADMIN"})
        self.assertEqual(r.status_code, 401)
        # 新密码强度不够
        r = c.post(self.password_url, {"old_password": "password", "password": "admin"})
        self.assertEqual(r.status_code, 400)
