# 此代码被 users.tests 引用，在 python3 manage.py test 中会一并测试
from django.test import SimpleTestCase

from .validators import is_email


class TestIsEmail(SimpleTestCase):
    testcases = [
        ["", False],
        ["@", False],
        ["1@2", True],
        ["@qq.com", False],
        ["233@", False],
        ["123$456@qq.com", False],
        ["123@qq.com", True],
        ["123@qq.com.cn", True],
        ["123@qwertyuiop.com", True],
        ["123.456@qq.com", True]
    ]

    def test_is_email(self):
        for tc in self.testcases:
            self.assertEqual(is_email(tc[0]), tc[1], "str: " + tc[0])


# class TestIsValidUsername(SimpleTestCase):
#     testcases = [
#         ["", False],
#         ["1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM_-", True],
#         ["123", True],
#         ["123@", False],
#         ["@123", False],
#         ["12@3", False],
#         ["1+3", False],
#         ["1=2", False],
#         ["123!", False],
#         ["lyh543", True],
#         ["usetc-msc", True]
#     ]
#
#     def test_is_valid_username(self):
#         for tc in self.testcases:
#             self.assertEqual(is_valid_username(tc[0]), tc[1], "str: " + tc[0])
