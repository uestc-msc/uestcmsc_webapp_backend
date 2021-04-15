from utils.tests import OnedriveTestCase
from django.test.client import Client

class ActivityFileTest(OnedriveTestCase):
    filepath = 'static/ruanweiwei.png'

    def test_upload_activity_file(self):
        cilent = Client()
        self.upload_file()
