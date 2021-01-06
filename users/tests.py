from django.test import TestCase, Client
from utils.tests import tester_signup, tester_login, HTTP_USER_AGENT
from django.contrib.auth.models import User
from time import sleep


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

        r = tester_signup('admin', 'adminadmin', 'Admin', '1234567890123456')
        self.assertEqual(r.status_code, 400)
        error_argument = set(eval(r.content).keys())
        self.assertEqual(error_argument, {'username'})


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
        self.assertEqual(r.renderer_context["request"].user, self.admin_user)

        r = tester_login('admin@example.com', 'adminadmin')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.renderer_context["request"].user, self.admin_user)

    def test_login_with_less_argument(self):
        r = Client().post('/users/login/')
        self.assertEqual(r.status_code, 401)

        r = Client().post('/users/login/')
        self.assertEqual(r.status_code, 401)

        r = Client().get('/users/login/')
        self.assertEqual(r.status_code, 405)

        r = Client().post('/users/login/', {"username": "admin@example.com"})
        self.assertEqual(r.status_code, 401)

        r = Client().post('/users/login/', {"password": "adminadmin"})
        self.assertEqual(r.status_code, 401)

        r = tester_login('admin', '')
        self.assertEqual(r.status_code, 401)

        r = tester_login('', 'admin')
        self.assertEqual(r.status_code, 401)

    def test_login_with_wrong_authentication(self):
        r = tester_login('user@example.com', 'useruser')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.renderer_context["request"].user, self.another_user)

        r = tester_login('user@example.com', 'admin')
        self.assertEqual(r.status_code, 401)

        r = tester_login('admin@example.com', 'USERUSER')
        self.assertEqual(r.status_code, 401)

        r = tester_login('admin@example.com', 'adminadmin')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.renderer_context["request"].user, self.admin_user)

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
        self.assertEqual(r.renderer_context["request"].user, self.admin_user)

        r = tester_login('user@example.com', 'useruser', c)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.renderer_context["request"].user, self.another_user)

        r = tester_login('wrong', 'wrongpassword', c)
        self.assertEqual(r.status_code, 401)

        r = tester_login('admin@example.com', 'adminadmin', c)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.renderer_context["request"].user, self.admin_user)


# 注销相关测试
class LogoutTest(TestCase):
    def test_log_out(self):
        tester_signup("admin@example.com", "adminadmin")
        r = Client().get('/users/logout/')
        self.assertEqual(r.status_code, 401)

        r = tester_login("admin@example.com", "adminadmin")
        self.assertEqual(r.renderer_context["request"].user, User.objects.first())
        r = r.client.get('/users/logout/')
        self.assertEqual(r.status_code, 204)
        self.assertEqual(r.renderer_context["request"].user.is_authenticated, False)


class ForgetPasswordEmailTest(TestCase):
    fake_email = "test@example.com"

    def test_invalid_input(self):
        c = Client()
        r = tester_signup(self.fake_email, 'adminadmin', 'Admin', '20210101', c)
        self.assertEqual(r.renderer_context["request"].user, User.objects.first())

        r = c.post('/users/resetpassword', {"email": "12312313"})
        self.assertEqual(r.status_code, 400)
        r = c.post('/users/resetpassword', {"email": "Admin"})
        self.assertEqual(r.status_code, 400)
        r = c.post('/users/resetpassword', {"email": "admin"})
        self.assertEqual(r.status_code, 200)

    # 由于该过程需要交互，所以不用重复测
    def test_forget_password(self):
        self.email = input("请输入邮箱：").strip()
        c = Client()
        r = tester_signup(self.email, 'adminadmin', 'Admin', '20210101', c)
        self.assertEqual(r.renderer_context["request"].user, User.objects.first())
        r = c.get('/')
        self.assertEqual(r.renderer_context["request"].user, User.objects.first())

        c2 = Client()
        r = c2.post('/users/resetpassword', {"email": self.email})
        self.assertEqual(r.status_code, 200)
        verification_code = input('已发送验证码至 ' + self.email + '，请输入验证码').strip()
        r = c.post('/user/resetpassword', {
            "email": self.email,
            "verification_code": verification_code,
            "new_password": "new_admin_password"
        })
        self.assertEqual(r.status_code, 200)

        r = c.get('/')
        self.assertEqual(r.renderer_context["request"].user.is_authenticated, False)  # 此时第一个 Client 理应被下线

        r = tester_login('admin', 'new_admin_password')
        self.assertEqual(r.status_code, 401)
        r = tester_login(self.email, 'new_admin_password')
        self.assertEqual(r.status_code, 401)

        r = tester_login('admin', 'adminadmin')
        self.assertEqual(r.status_code, 200)
        r = tester_login(self.email, 'adminadmin')
        self.assertEqual(r.status_code, 200)

    # 每测一次要等 60s，所以也不用重复测
    def test_forget_password_ddos(self):
        c = Client()
        r = tester_signup(self.fake_email, 'adminadmin', 'Admin', '20210101', c)

        r = c.post('/users/resetpassword', {"email": self.fake_email})
        self.assertEqual(r.status_code, 200)

        for i in range(10):
            r = c.post('/users/resetpassword', {"email": self.fake_email})
            self.assertEqual(r.status_code, 403)

        print("wait to send another email...")
        sleep(60)
        r = c.post('/users/resetpassword', {"email": self.fake_email})
        self.assertEqual(r.status_code, 200)
