from datetime import timedelta
from random import random

from django.test import TestCase, Client
from django.utils.timezone import now

from users.models import ResetPasswordRequest
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

