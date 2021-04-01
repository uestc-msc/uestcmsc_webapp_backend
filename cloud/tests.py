from django.test import SimpleTestCase
from django.urls import reverse

from cloud.onedrive.auth import OnedriveAuthentication


class OnedriveLoginCallbackLinkTest(SimpleTestCase):
    def test_login_callback_link(self):
        self.assertEqual(reverse('onedrive_login_callback'), OnedriveAuthentication.redirect_path)