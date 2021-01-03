from django.test import TestCase, Client
from utils.tests import tester_signup
from django.contrib.auth.models import User

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