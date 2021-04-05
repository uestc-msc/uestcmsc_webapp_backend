
from unittest import skipIf

from django.test import SimpleTestCase, Client, TestCase
from django.urls import reverse

from cloud.onedrive.auth import OnedriveAuthentication
from cloud.onedrive.cache import get_refresh_token

no_refresh_token = get_refresh_token() is None

onedrive_status_url = reverse('onedrive_status')
onedrive_file_url = reverse('onedrive_file')


class OnedriveLoginCallbackLinkTest(SimpleTestCase):
    def test_login_callback_link(self):
        self.assertEqual(reverse('onedrive_login_callback'), OnedriveAuthentication.redirect_path)



@skipIf(no_refresh_token, "Onedrive Not Login")
class OnedriveStatusTest(TestCase):
    def test_get_onedrive_status(self):
        client = Client()
        response = client.get(onedrive_status_url)
        self.assertEqual(response.json()['status'], 'active')
