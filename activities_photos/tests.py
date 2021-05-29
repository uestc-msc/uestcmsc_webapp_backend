from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.timezone import now

from activities.models import Activity
from utils.tester import OnedriveTestCase
from django.test.client import Client

activity_photo_list_url = reverse('activity_photo_list')
activity_photo_detail_url = lambda id: reverse('activity_photo_detail', args=[id])


class ActivityPhotoTest(OnedriveTestCase):
    filepath = 'static/ruanweiwei.png'

    def setUp(self):
        # 设置用户的权限
        self.superuser = User.objects.create_user(username="superuser@aka.ms", first_name="superuser",
                                                  is_superuser=True)
        self.admin = User.objects.create_user(username="admin@aka.ms", first_name="admin", is_staff=True)
        self.simple_user = User.objects.create_user(username="a_user@aka.ms", first_name="user")
        self.presenter = User.objects.create_user(username="presenter@aka.ms", first_name="presenter")
        self.another_presenter = User.objects.create_user(username="another_presenter@aka.ms",
                                                          first_name="another_presenter")
        self.ids = list(map(lambda u: u.id, User.objects.all()))

        self.activity = Activity.objects.create(title="First Activity", datetime=now(), location="MSFT")
        self.activity.presenter.add(self.presenter, self.another_presenter)

    # 完整的上传、删除过程
    def test_upload_activity_photo_whole_process(self):
        client = Client()
        client.force_login(self.superuser)
        file_id = self.upload_file(self.filepath, client)
        response = client.post(activity_photo_list_url, {"file_id": file_id, "activity_id": self.activity.id})
        self.assertEqual(response.status_code, 201)  # 上传成功
        self.assertEqual(self.activity.photo.count(), 1)
        # 验证信息正确
        content = response.json()
        self.assertEqual(content['id'], file_id)
        self.assertEqual(int(content['activity_id']), self.activity.id)
        self.assertEqual(content['uploader']['id'], self.superuser.id)
        with open(self.filepath, 'rb') as f:
            self.assertEqual(content['size'], len(f.read()))
        self.assertEqual(not content["download_link"], False)
        # 删除照片
        response = client.delete(activity_photo_detail_url(file_id))
        self.assertEqual(response.status_code, 204)  # 删除成功
        self.assertEqual(self.activity.photo.count(), 0)

    # 剩下的测试咕咕咕了
