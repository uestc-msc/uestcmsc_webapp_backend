from django.test import SimpleTestCase, Client
from django.urls import reverse

from cloud.onedrive import *
from cloud.onedrive.api.auth import OnedriveAuthentication
from utils.tester import OnedriveTestCase

onedrive_status_url = reverse('onedrive_status')
onedrive_file_url = reverse('onedrive_file')


class OnedriveLoginCallbackLinkTest(SimpleTestCase):
    def test_login_callback_link(self):
        self.assertEqual(reverse('onedrive_login_callback'), OnedriveAuthentication.redirect_path)


class OnedriveStatusTest(OnedriveTestCase):
    def test_get_onedrive_status(self):
        client = Client()
        response = client.get(onedrive_status_url)
        self.assertEqual(response.json()['status'], 'active')


class OnedriveBasicTest(OnedriveTestCase):
    def test_variables_are_set_correctly(self):
        self.assertRegexpMatches(onedrive_approot.uri, '_test')
        self.assertRegexpMatches(onedrive_activity_directory.uri, '_test')
        self.assertRegexpMatches(onedrive_temp_directory.uri, '_test')
