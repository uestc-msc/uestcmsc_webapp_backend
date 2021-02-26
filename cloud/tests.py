from django.test import SimpleTestCase
from django.urls import reverse

from cloud.onedrive import onedrive


class OnedriveLoginCallbackLinkTest(SimpleTestCase):
    def test_login_callback_link(self):
        self.assertEqual(reverse('onedrive_login_callback'), onedrive.redirect_path)