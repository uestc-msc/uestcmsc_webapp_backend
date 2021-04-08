from django.contrib.auth.models import User, AnonymousUser
from django.test import TestCase, Client
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.timezone import now

from activities.models import Activity
from activities.tests import activity_detail_url
from utils.tests import tester_create_activity

activity_link_list_url = reverse('activity_link_list')
activity_link_detail_url = lambda id: reverse('activity_link_detail', args=[id])


class ActivityLinkListTest(TestCase):
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

    def test_create_activity_link(self):
        client = Client()
        client.force_login(self.superuser)
        response = client.post(activity_link_list_url, {
            "activity_id": self.activity.id,
            "url": "https://uestc-msc.com/"
        }, content_type='application/json')
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(self.activity.link.count(), 1)  # 活动成功写入数据库
        self.assertEqual(self.activity.link.first().url, "https://uestc-msc.com/")  # 比较 POST 值和数据库中的值

    def test_create_activity_link_unauthorized(self):
        user_permissions = [  # 以六种用户身份去 post
            [AnonymousUser, False],
            [self.superuser, True],
            [self.admin, True],
            [self.simple_user, False],
            [self.presenter, True],
            [self.another_presenter, True]
        ]
        for user, permission in user_permissions:
            link = get_random_string(20)

            client = Client()
            if user != AnonymousUser:
                client.force_login(user)
            response = client.post(activity_link_list_url, {
                "activity_id": self.activity.id,
                "url": link
            }, content_type='application/json')

            if permission:
                self.assertEqual(response.status_code, 201, f"user={user}")
            else:
                self.assertEqual(response.status_code, 403, f"user={user}")

    def test_create_activity_link_with_empty_field(self):
        client = Client()
        client.force_login(self.presenter)
        complete_data = {
            "activity_id": self.activity.id,
            "url": "https://uestc-msc.com/"
        }
        for missing_field in complete_data.keys():  # 两种数据各缺一遍。都不能成功创建
            incomplete_data = complete_data.copy()
            incomplete_data.pop(missing_field)
            response = client.post(activity_link_list_url, incomplete_data, content_type='application/json')
            self.assertEqual(response.status_code, 400)

        response = client.post(activity_link_list_url, complete_data, content_type='application/json')
        self.assertEqual(response.status_code, 201)  # 而正确数据是可以注册的

    def test_create_activity_link_with_invalid_field(self):
        correct_example = {
            "activity_id": self.activity.id,
            "url": "https://uestc-msc.com/"
        }

        field_and_invalid_example = [
            ['activity_id', ''],
            ['url', 'a' * 10000],
        ]
        self.assertEqual(self.activity.link.count(), 0)  # 没有链接
        client = Client()
        client.force_login(self.superuser)
        for field, example in field_and_invalid_example:
            incorrect_example = correct_example.copy()
            incorrect_example[field] = example
            response = client.post(activity_link_list_url,
                                   data=incorrect_example,
                                   content_type='application/json')
            self.assertEqual(response.status_code, 400)  # 返回 400
            self.assertEqual(self.activity.link.count(), 0)  # 没有链接

        # 活动不存在，返回 404
        response = client.post(activity_link_list_url, data={"activity_id": 2333, "url": "https://uestc-msc.com/"},
                               content_type='application/json')
        self.assertEqual(response.status_code, 404)  # 返回 400
        self.assertEqual(self.activity.link.count(), 0)  # 没有链接

    def test_get_activity_link_list(self):
        links = {'233333333', 'https://uestc-msc.com/', 'UESTCMSC', ''}
        for link in links:
            self.activity.link.create(url=link)
        self.assertEqual(self.activity.link.count(), 4)

        client = Client()
        response = client.get(activity_detail_url(self.activity.id))
        response_links = set(map(lambda l: l['url'], response.json()['link']))
        self.assertSetEqual(response_links, links)


class ActivityLinkDetailTest(TestCase):
    def setUp(self):
        # 设置用户的权限
        self.superuser = User.objects.create_user(username="superuser@aka.ms", first_name="superuser",
                                                  is_superuser=True)
        self.admin = User.objects.create_user(username="admin@aka.ms", first_name="admin", is_staff=True)
        self.simple_user = User.objects.create_user(username="a_user@aka.ms", first_name="user")
        self.presenter = User.objects.create_user(username="presenter@aka.ms", first_name="presenter")
        self.another_presenter = User.objects.create_user(username="another_presenter@aka.ms",
                                                          first_name="another_presenter")

        tester_create_activity('First Salon', '2020-01-01T00:00:00.000Z', 'MS Shanghai',
                               [self.presenter.id, self.another_presenter.id])
        self.activity = Activity.objects.first()
        self.activity.link.create(url='https://uestc-msc.com/')

    def test_get(self):
        client = Client()
        link_id = self.activity.link.first().id
        response = client.get(activity_link_detail_url(link_id))
        self.assertEqual(response.status_code, 200)  # 未登录用户访问，返回 200
        self.assertEqual(response.json()['url'], 'https://uestc-msc.com/')

    def test_get_404(self):
        client = Client()
        fake_link_id = self.activity.link.first().id + 1
        response = client.get(activity_link_detail_url(fake_link_id))
        self.assertEqual(response.status_code, 404)

    # 只测试 patch，该测试也包含了 patch 成功
    def test_patch_unauthorized(self):
        link_id = self.activity.link.first().id

        user_permissions = [  # 以六种用户身份去遍历
            [AnonymousUser, False],
            [self.superuser, True],
            [self.admin, True],
            [self.simple_user, False],
            [self.presenter, True],
            [self.another_presenter, True]
        ]

        for user, permission in user_permissions:
            client = Client()
            if user != AnonymousUser:
                client.force_login(user)

            response = client.patch(activity_link_detail_url(link_id),
                                    data={"url": 'you-have-been-modified'},
                                    content_type='application/json')
            self.assertEqual(response.status_code == 200, permission,
                             f"user={user}, status_code={response.status_code}")
            self.assertEqual(response.status_code != 403, permission,
                             f"user={user}, status_code={response.status_code}")
            self.assertEqual(self.activity.link.first().url == 'you-have-been-modified', permission, f"user={user}")
            link = self.activity.link.first()
            link.url = 'https://uestc-msc.com/'  # 要改回去
            link.save()

    def test_patch_404(self):
        client = Client()
        client.force_login(self.superuser)
        response = client.patch(activity_link_detail_url(23333),
                                data={"url": 'you-have-been-modified'},
                                content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_patch_with_invalid_value(self):
        field_and_invalid_example = [
            ['id', self.activity.id],
            ['url', 'a' * 10000],
        ]
        client = Client()
        client.force_login(self.superuser)
        id = self.activity.link.first().id
        for field, example in field_and_invalid_example:
            response = client.patch(activity_link_detail_url(id),
                                    data={field: example},
                                    content_type='application/json')
            if field == 'id':
                self.assertEqual(self.activity.link.first().url, 'https://uestc-msc.com/')
            else:
                self.assertEqual(response.status_code, 400, f"{field}={example}")  # 返回 400
                response = client.get(activity_link_detail_url(id))
                self.assertNotEqual(response.json()[field], example)  # GET 的数据并没有被修改

    def test_delete(self):
        client = Client()
        client.force_login(self.superuser)
        id = self.activity.link.first().id
        old_count = self.activity.link.count()
        response = client.delete(activity_link_detail_url(id))
        self.assertEqual(response.status_code, 204)  # 删除成功 返回 204
        self.assertEqual(self.activity.link.count(), old_count - 1)  # 活动数量--

    def test_delete_404(self):
        client = Client()
        client.force_login(self.superuser)
        old_count = self.activity.link.count()
        response = client.delete(activity_link_detail_url(23333))
        self.assertEqual(response.status_code, 404)  # 活动不存在 返回 404
        self.assertEqual(self.activity.link.count(), old_count)  # 活动数量不变

    def test_delete_unauthorized(self):
        user_permissions = [  # 以六种用户身份去遍历
            [AnonymousUser, False],
            [self.superuser, True],
            [self.admin, True],
            [self.simple_user, False],
            [self.presenter, True],
            [self.another_presenter, True]
        ]

        for user, permission in user_permissions:
            link = self.activity.link.create(url="test")
            client = Client()
            if user != AnonymousUser:
                client.force_login(user)
            response = client.delete(activity_link_detail_url(link.id))
            if permission:
                self.assertEqual(response.status_code, 204, f"user={user}")
            else:
                self.assertEqual(response.status_code, 403, f"user={user}")
                link.delete()
