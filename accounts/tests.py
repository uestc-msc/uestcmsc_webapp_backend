from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from django.utils.timezone import now

from users.models import ResetPasswordRequest, UserProfile
from utils import generate_uuid
from utils import tester_signup, assertUserDetailEqual, tester_login, pop_token_from_virtual_mailbox

signup_url = reverse('signup')
login_url = reverse('login')
logout_url = reverse('logout')
forget_password_url = reverse('forget_password')
reset_password_url = reverse('reset_password')
user_detail_url = lambda id: reverse('user_detail', args={id: id})


# 注册相关测试
class SignUpTests(TestCase):
    def test_sign_up(self):
        response = tester_signup()
        self.assertEqual(User.objects.count(), 1)
        assertUserDetailEqual(self, response.content, User.objects.first())

    def test_sign_up_with_empty_field(self):
        response = Client().post(signup_url)
        self.assertEqual(response.status_code, 400)
        error_argument = set(eval(response.content).keys())
        self.assertSetEqual(error_argument, {'username', 'password', 'first_name', 'student_id'})

        response = tester_signup('admin@example.com', 'adminadmin', '', '123456')
        self.assertEqual(response.status_code, 400)
        error_argument = set(eval(response.content).keys())
        self.assertSetEqual(error_argument, {'first_name'})

        response = tester_signup('admin@example.com', '', 'ad', '123456')
        self.assertEqual(response.status_code, 400)
        error_argument = set(eval(response.content).keys())
        self.assertSetEqual(error_argument, {'password'})

        response = tester_signup('', 'adminadmin', 'ad', '123456')
        self.assertEqual(response.status_code, 400)
        error_argument = set(eval(response.content).keys())
        self.assertSetEqual(error_argument, {'username'})

        response = tester_signup('admin@example.com', 'adminadmin', 'ad', '')
        self.assertEqual(response.status_code, 400)
        error_argument = set(eval(response.content).keys())
        self.assertSetEqual(error_argument, {'student_id'})

    def test_sign_up_with_invalid_field(self):
        response = tester_signup('admin@example.com', 'adminadmin', 'ad', '123456')
        self.assertEqual(response.status_code, 201)

        response = tester_signup('admin1@example.com', 'adminadmin', 'ad', '123456')
        self.assertEqual(response.status_code, 400)
        error_argument = set(eval(response.content).keys())
        self.assertSetEqual(error_argument, {'student_id'})

        response = tester_signup('admin5@example.com', 'adminadmin', 'ad', '3e5')
        self.assertEqual(response.status_code, 400)
        error_argument = set(eval(response.content).keys())
        self.assertSetEqual(error_argument, {'student_id'})

        response = tester_signup('admin3@example.com', 'admina', 'ad', '1234567')
        self.assertEqual(response.status_code, 201)

        response = tester_signup('admin4@example.com', 'admin', 'ad', '12345678')
        self.assertEqual(response.status_code, 400)
        error_argument = set(eval(response.content).keys())
        self.assertSetEqual(error_argument, {'password'})

        response = tester_signup('admin@example.com', 'adminadmin', 'ad', '12345678')
        self.assertEqual(response.status_code, 400)
        error_argument = set(eval(response.content).keys())
        self.assertSetEqual(error_argument, {'username'})

        response = tester_signup('admin6@example.com', 'adminadmin', 'ad', '1234567890')
        self.assertEqual(response.status_code, 201)

        response = tester_signup('uestcmsc@outlook.com', 'passw0rd', '电子科技大学微软学生俱乐部', '20201024')
        self.assertEqual(response.status_code, 201)

        response = tester_signup('admin', 'adminadmin', 'Admin', '1234567890123456')
        self.assertEqual(response.status_code, 400)
        error_argument = set(eval(response.content).keys())
        self.assertSetEqual(error_argument, {'username'})

    def test_wechat_user_sign_up_and_bind_account(self):
        u = User.objects.create(username='qwerty',
                                first_name='wechat_user')
        up = UserProfile.objects.create(user=u,
                                        student_id='6789')

        response = tester_signup('wechat_user@example.com', 'wechat_user0', 'wechat_user', '6789')
        self.assertEqual(response.status_code, 200)
        u.refresh_from_db()
        self.assertEqual(u.username, 'wechat_user@example.com')
        assertUserDetailEqual(self, response.content, u)

    def test_wechat_user_sign_up_with_invalid_field(self):
        u = User.objects.create_user(username='qwerty',
                                     first_name='wechat_user')
        up = UserProfile.objects.create(user=u,
                                        student_id='6789')

        response = tester_signup('wechat_user@example.com', 'wechat_user0', 'wechatuser', '6789')  # 姓名错误
        self.assertEqual(response.status_code, 400)
        response = tester_signup('wechat_user@example.com', 'wechat_user0', 'wechat_user', '67890')  # 学号错误，注册为别的用户
        self.assertEqual(response.status_code, 201)
        User.objects.get(username='wechat_user@example.com').delete()

        u.set_password('23333')
        u.save()
        response = tester_signup('wechat_user@example.com', 'wechat_user0', 'wechat_user', '6789')  # 信息正确，但该用户已经被注册
        self.assertEqual(response.status_code, 400)


# 登录相关测试
class LoginTest(TestCase):
    def setUp(self):
        response = tester_signup('admin@example.com', 'adminadmin', 'Admin', '20210101')
        self.admin_user = User.objects.get(username='admin@example.com')
        tester_signup('user@example.com', 'useruser', 'User', '20210104')
        self.another_user = User.objects.get(username='user@example.com')

    def test_login_correctly(self):
        response = tester_login('admin@example.com', 'adminadmin')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.wsgi_request.user, self.admin_user)
        self.admin_user.refresh_from_db()
        assertUserDetailEqual(self, response.content, self.admin_user)  # 响应报文和实际数据相同

        response = tester_login('admin@example.com', 'adminadmin')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.wsgi_request.user, self.admin_user)
        self.admin_user.refresh_from_db()
        assertUserDetailEqual(self, response.content, self.admin_user)  # 响应报文和实际数据相同

    def test_login_with_less_argument(self):
        response = Client().post(login_url)
        self.assertEqual(response.status_code, 401)

        response = Client().post(login_url)
        self.assertEqual(response.status_code, 401)

        response = Client().get(login_url)
        self.assertEqual(response.status_code, 405)

        response = Client().post(login_url, {"username": "admin@example.com"})
        self.assertEqual(response.status_code, 401)

        response = Client().post(login_url, {"password": "adminadmin"})
        self.assertEqual(response.status_code, 401)

        response = tester_login('admin', '')
        self.assertEqual(response.status_code, 401)

        response = tester_login('', 'admin')
        self.assertEqual(response.status_code, 401)

    def test_login_with_invalid_authentication(self):
        response = tester_login('user@example.com', 'useruser')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.wsgi_request.user, self.another_user)

        response = tester_login('user@example.com', 'admin')
        self.assertEqual(response.status_code, 401)

        response = tester_login('admin@example.com', 'USERUSER')
        self.assertEqual(response.status_code, 401)

        response = tester_login('admin@example.com', 'adminadmin')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.wsgi_request.user, self.admin_user)

        response = tester_login('admin@example.com', 'admin')
        self.assertEqual(response.status_code, 401)

        response = tester_login('admin', 'adminadmin')
        self.assertEqual(response.status_code, 401)

        response = tester_login('admin@example.com', 'useruser')
        self.assertEqual(response.status_code, 401)

        response = tester_login('user@example.com', 'adminadmin')
        self.assertEqual(response.status_code, 401)

    def test_login_by_switch_user(self):
        client = Client()
        response = tester_login('admin@example.com', 'adminadmin', client)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.wsgi_request.user, self.admin_user)

        response = tester_login('user@example.com', 'useruser', client)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.wsgi_request.user, self.another_user)

        response = tester_login('wrong', 'wrongpassword', client)
        self.assertEqual(response.status_code, 401)

        response = tester_login('admin@example.com', 'adminadmin', client)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.wsgi_request.user, self.admin_user)


# 登出相关测试
class LogoutTest(TestCase):
    def test_log_out(self):
        tester_signup("admin@example.com", "adminadmin")
        response = Client().post(logout_url)
        self.assertEqual(response.status_code, 401)

        response = tester_login("admin@example.com", "adminadmin")
        self.assertEqual(response.wsgi_request.user, User.objects.first())
        response = response.client.post(logout_url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.wsgi_request.user.is_authenticated, False)


# 重置密码相关测试
class ResetPasswordTest(TestCase):
    email = "admin@example.com"
    password = "adminadmin"

    def setUp(self):
        tester_signup(self.email, self.password, 'Admin', '20210101')
        self.user = User.objects.first()

    # Django test 中不会真的发送邮件
    # 文档：https://docs.djangoproject.com/zh-hans/3.1/topics/testing/tools/#email-services
    def test_forget_password_whole_process(self):
        client = Client()
        response = tester_login(self.email, self.password, client)
        self.assertEqual(response.wsgi_request.user, self.user)
        response = client.get('/')
        self.assertEqual(response.wsgi_request.user, self.user)

        c2 = Client()
        response = c2.post(forget_password_url, {"email": self.email})
        self.assertEqual(response.status_code, 202)

        token = pop_token_from_virtual_mailbox(self)
        response = c2.post(reset_password_url, {
            "token": token
        })
        self.assertEqual(response.status_code, 200)  # token 有效

        response = c2.post(reset_password_url, {
            "token": token,
            "new_password": "new_password"
        })
        self.assertEqual(response.status_code, 204)  # 修改成功

        response = client.get('/')
        self.assertEqual(response.wsgi_request.user.is_authenticated, False)  # 此时第一个 Client 理应被下线
        response = c2.get('/')
        self.assertEqual(response.wsgi_request.user.is_authenticated, False)  # 此时第二个 Client 也应该不在线

        response = tester_login(self.email, self.password)
        self.assertEqual(response.status_code, 401)

        response = tester_login(self.email, 'new_password')
        self.assertEqual(response.status_code, 200)

        response = tester_login(self.email, self.password)
        self.assertEqual(response.status_code, 401)

    def test_forget_email_with_invalid_field(self):
        client = Client()
        response = tester_login(self.email, self.password, client)
        self.assertEqual(response.wsgi_request.user, self.user)

        response = client.post(forget_password_url, {"email": "12312313"})
        self.assertEqual(response.status_code, 400)
        response = client.post(forget_password_url, {"email": "Admin"})
        self.assertEqual(response.status_code, 400)
        response = client.post(forget_password_url, {"email": "example@example.com"})
        self.assertEqual(response.status_code, 400)
        response = client.post(forget_password_url, {"email": self.email})
        self.assertEqual(response.status_code, 202)

    def test_validate_token_with_invalid_field(self):
        tester_signup("another@example.com", "anotheruser", "another", "20201231")
        anotheruser = User.objects.filter(username="another@example.com").first()
        self.assertIsNotNone(anotheruser)
        client = Client()
        response = client.post(forget_password_url, {"email": self.email})
        self.assertEqual(response.status_code, 202)
        user_token = pop_token_from_virtual_mailbox(self)

        # 假 token
        response = client.post(reset_password_url, {
            "token": generate_uuid(),
            "new_password": "new_password"
        })
        self.assertEqual(response.status_code, 403)

        response = client.post(reset_password_url, {
            "token": generate_uuid()
        })
        self.assertEqual(response.status_code, 403)
        # 过期 token
        expired_token = generate_uuid()
        ResetPasswordRequest.objects.create(user=self.user, token=expired_token, request_time=now() - timedelta(days=2),
                                            ipv4addr="127.0.0.1")
        response = client.post(reset_password_url, {
            "token": expired_token
        })
        self.assertEqual(response.status_code, 403)
        # 弱密码
        response = client.post(reset_password_url, {
            "token": user_token,
            "new_password": "pd"
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(eval(response.content)['detail'], '新密码不合法')
        # 重复使用 token
        response = client.post(reset_password_url, {
            "token": user_token,
            "new_password": "new_password"
        })
        self.assertEqual(response.status_code, 204)
        response = client.post(reset_password_url, {
            "token": user_token,
            "new_password": "new_password"
        })
        self.assertEqual(response.status_code, 403)

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
            response = Client().post(forget_password_url, {"email": self.user.username})
            self.assertEqual(response.status_code, 202)
            response = Client().post(forget_password_url, {"email": self.user.username})
            self.assertEqual(response.status_code, 403)
            # 将最近一封改为更远的时间，重新发两封，第一封成功第二封失败
            rpr = ResetPasswordRequest.objects.order_by('request_time').last()
            rpr.request_time = now() - delta
            rpr.save()
            response = Client().post(forget_password_url, {"email": self.user.username})
            self.assertEqual(response.status_code, 202)
            self.assertEqual(ResetPasswordRequest.objects.filter(request_time__lt=now() - timedelta(days=1)).count(),
                             0)  # 保证过期的邮件有被清除
            response = Client().post(forget_password_url, {"email": self.user.username})
            self.assertEqual(response.status_code, 403)
            ResetPasswordRequest.objects.all().delete()
