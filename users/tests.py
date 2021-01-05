from django.test import TestCase, Client
from utils.tests import tester_signup, tester_login, HTTP_USER_AGENT
from django.contrib.auth.models import User
from time import sleep


# 注册相关测试
class SignUpTests(TestCase):
    def test_sign_up_with_empty_field(self):
        r = Client().post('/users/signup/')
        self.assertEqual(r.status_code, 400)
        self.assertEqual(eval(r.content), 'username should not be empty.\n'
                                          'password should not be empty.\n'
                                          'first_name should not be empty.\n'
                                          'email should not be empty.\n'
                                          'student_id should not be empty.\n')

        r = tester_signup('', 'adminadmin', 'ad', 'admin@example.com', '123456')
        self.assertEqual(r.status_code, 400)
        self.assertEqual(eval(r.content), 'username should not be empty.\n')

        r = tester_signup('admin', 'adminadmin', '', 'admin@example.com', '123456')
        self.assertEqual(r.status_code, 400)
        self.assertEqual(eval(r.content), 'first_name should not be empty.\n')

        r = tester_signup('admin', '', 'ad', 'admin@example.com', '123456')
        self.assertEqual(r.status_code, 400)
        self.assertEqual(eval(r.content), 'password should not be empty.\n')

        r = tester_signup('admin', 'adminadmin', 'ad', '', '123456')
        self.assertEqual(r.status_code, 400)
        self.assertEqual(eval(r.content), 'email should not be empty.\n')

        r = tester_signup('admin', 'adminadmin', 'ad', 'admin@example.com', '')
        self.assertEqual(r.status_code, 400)
        self.assertEqual(eval(r.content), 'student_id should not be empty.\n')

    def test_sign_up_with_invalid_field(self):
        r = tester_signup('admin', 'adminadmin', 'ad', 'admin@example.com', '123456')
        self.assertEqual(r.status_code, 200)
        r = tester_signup('admin', 'adminadmin', 'ad', 'admin1@example.com', '123456')
        self.assertEqual(r.status_code, 400)
        self.assertEqual(eval(r.content), 'username already exists.\nstudent_id already exists.\n')

        r = tester_signup('admin5', 'adminadmin', 'ad', 'admin5@example.com', '3e5')
        self.assertEqual(r.status_code, 400)
        self.assertEqual(eval(r.content), 'student_id should be number.\n')

        r = tester_signup('admin3', 'admina', 'ad', 'admin3@example.com', '1234567')
        self.assertEqual(r.status_code, 200)
        r = tester_signup('admin4', 'admin', 'ad', 'admin4@example.com', '12345678')
        self.assertEqual(r.status_code, 400)
        self.assertEqual(eval(r.content), 'password should be at least 6 letters.\n')

        r = tester_signup('admin2', 'adminadmin', 'ad', 'admin@example.com', '12345678')
        self.assertEqual(r.status_code, 400)
        self.assertEqual(eval(r.content), 'email already exists.\n')
        r = tester_signup('admin5', 'adminadmin', 'ad', '@', '123456789')
        self.assertEqual(r.status_code, 400)
        self.assertEqual(eval(r.content), 'email is not invalid.\n')

        r = tester_signup('admin6', 'adminadmin', 'ad', 'admin6@example.com', '1234567890')
        self.assertEqual(r.status_code, 200)


# 登录相关测试
class LogInTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        r = tester_signup('admin', 'adminadmin', 'Admin', 'admin@example.com', '20210101')
        cls.admin_user = User.objects.get(username='admin')
        tester_signup('user', 'useruser', 'User', 'user@example.com', '20210104')
        cls.another_user = User.objects.get(username='user')

    def test_login_correctly(self):
        r = tester_login('admin@example.com', 'adminadmin')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.user, self.admin_user)

        r = tester_login('admin', 'adminadmin')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.user, self.admin_user)

    def test_log_in_with_less_argument(self):
        r = Client().post('/users/login/')
        self.assertEqual(r.status_code, 401)

        r = Client().post('/users/login/', {"username": "admin"})
        self.assertEqual(r.status_code, 401)

        r = Client().post('/users/login/', {"username": "admin@example.com"})
        self.assertEqual(r.status_code, 401)

        r = Client().post('/users/login/', {"password": "adminadmin"})
        self.assertEqual(r.status_code, 401)

        r = tester_login('admin', '')
        self.assertEqual(r.status_code, 401)

        r = tester_login('', 'admin')
        self.assertEqual(r.status_code, 401)

    def test_log_in_with_wrong_authentication(self):
        r = tester_login('Admin', 'adminadmin')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.user, self.admin_user)

        r = tester_login('admin', 'admin')
        self.assertEqual(r.status_code, 401)

        r = tester_login('admin', 'ADMINADMIN')
        self.assertEqual(r.status_code, 401)

        r = tester_login('admin@example.com', 'adminadmin')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.user, self.admin_user)

        r = tester_login('admin', 'admin')
        self.assertEqual(r.status_code, 401)
        self.assertNotEqual(r.user, self.admin_user)

    def test_login_by_switch_user(self):
        c = Client()
        r = tester_login('admin', 'adminadmin', c)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.user, self.admin_user)

        r = tester_login('user', 'user', c)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.user, self.another_user)

        r = tester_login('wrong', 'wrongpassword', c)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.user.is_authenticated, False)

        r = tester_login('admin', 'adminadmin', c)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.user, self.admin_user)


class ForgetPasswordEmailTest(TestCase):
    email = "lyh543@outlook.com"
    fake_email = "test@example.com"

    def test_invalid_input(self):
        c = Client()
        r = tester_signup('admin', 'adminadmin', 'Admin', self.fake_email, '20210101', c)
        self.assertEqual(r.user, User.objects.first())

        r = c.post('/users/resetpassword', {"email": "12312313"})
        self.assertEqual(r.status_code, 400)
        r = c.post('/users/resetpassword', {"email": "Admin"})
        self.assertEqual(r.status_code, 400)
        r = c.post('/users/resetpassword', {"email": "admin"})
        self.assertEqual(r.status_code, 200)


    # 由于该过程需要交互，所以不用重复测
    def test_forget_password(self):
        c = Client()
        r = tester_signup('admin', 'adminadmin', 'Admin', self.email, '20210101', c)
        self.assertEqual(r.user, User.objects.first())
        r = c.get('/')
        self.assertEqual(r.user, User.objects.first())

        c2 = Client()
        r = c2.post('/users/resetpassword', {"email": self.email})
        self.assertEqual(r.status_code, 200)
        verification_code = input('已发送验证码至 ' + self.email + '，请输入验证码').strip()
        r = c.post('/user/resetpassword', {
            "email" :self.email,
            "verification_code": verification_code,
            "new_password": "new_admin_password"
        })
        self.assertEqual(r.status_code, 200)

        r = c.get('/')
        self.assertEqual(r.user.is_authenticated, False) # 此时第一个 Client 理应被下线

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
        r = tester_signup('admin', 'adminadmin', 'Admin', self.fake_email, '20210101', c)

        r = c.post('/users/resetpassword', {"email": self.fake_email})
        self.assertEqual(r.status_code, 200)

        for i in range(10):
            r = c.post('/users/resetpassword', {"email": self.fake_email})
            self.assertEqual(r.status_code, 403)

        print("wait to send another email...")
        sleep(60)
        r = c.post('/users/resetpassword', {"email": self.fake_email})
        self.assertEqual(r.status_code, 200)