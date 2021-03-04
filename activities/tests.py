import json
from math import ceil
from random import randrange
from typing import List, Dict
from unittest import mock

import pytz
from django.contrib.auth.models import User, AnonymousUser
from django.test import TestCase, Client
from django.urls import reverse
from datetime import datetime, timedelta

from django.utils.timezone import now

from activities.models import Activity
from users.models import UserProfile
from utils import Pagination
from utils.tester import tester_signup, tester_create_activity, tester_login, assertActivityDetailEqual, assertDatetimeEqual

activity_list_url = reverse('activity_list')
activity_detail_url = lambda id: reverse('activity_detail', args=[id])
activity_detail_admin_url = lambda id: reverse('activity_detail_admin', args=[id])
activity_check_in_url = lambda id: reverse('activity_check_in', args=[id])
activity_detail_admin_check_in_url = lambda id: reverse('activity_detail_admin_check_in', args=[id])


class ActivityListTest(TestCase):
    def check_order(self, results: List[Dict]):
        """
        检查 results 是否是按时间、地点降序排列的
        """
        date_time = list(map(lambda a: datetime.fromisoformat(a["datetime"]), results))
        self.assertEqual(sorted(date_time, reverse=True), date_time)

    def setUp(self):
        response = tester_signup()
        response = tester_signup("superuser@example.com", "supersuper", "superuser", "1297391")
        response = tester_signup("user@example.com", "useruser", "user", "1297392")
        response = tester_signup("anotheruser@example.com", "anotheruser", "anotheruser", "1297393")
        self.ids = list(map(lambda u: u.id, User.objects.all()))
        self.assertEqual(Activity.objects.count(), 0)

    def test_create_activity(self):
        client = Client()
        tester_login(client=client)
        date_time = now()
        response = tester_create_activity("First Activity", date_time, "MSFT", self.ids[0:2], client=client)
        self.assertEqual(response.status_code, 201, response.data)

        self.assertEqual(Activity.objects.count(), 1)  # 活动成功写入数据库
        # 比较 POST 值和数据库中的值
        activity = Activity.objects.first()
        self.assertEqual(activity.title, "First Activity")
        assertDatetimeEqual(self, activity.datetime, date_time)
        self.assertEqual(activity.location, "MSFT")
        presenter_ids = set(map(lambda u: u.id, activity.presenter.all()))
        self.assertSetEqual(presenter_ids, set(self.ids[0:2]))
        self.assertEqual(activity.check_in_open, True)
        self.assertEqual(bool(activity.check_in_code), True)
        self.assertEqual(activity.attender.count(), 0)
        # 比较数据库中的值和返回值
        assertActivityDetailEqual(self, response.content, activity)

    def test_create_activity_unauthorized(self):
        response = tester_create_activity(client=Client())
        self.assertEqual(response.status_code, 403)

    def test_activity_time_format(self):
        # 以下时间应当均等价，应当得到相同的输出
        testcases = [
            '2020-01-01T00:00:00.000Z',
            '2020-01-01T08:00:00.000+08:00',
            '2020-01-01T08:00:00.00',
            '2020-01-01T08:00',
            '2020-01-01 08:00',
            '2020-01-01 08:00+08:00'
        ]
        error_testcases = [
            '2020-01-01',
            '00:00',
            '2021-02-29 08:00+08:00',
            '2020-13-01 08:00+08:00',
            '2020-13-31 08:00+08:00',
            '2020-12-31 24:00+08:00',
        ]

        output = None
        for test_input in testcases:
            response = tester_create_activity(date_time=test_input)
            self.assertEqual(response.status_code, 201)
            result = response.json()['datetime']
            if output is None:
                output = result
            else:
                self.assertEqual(result, output)

        for error_input in error_testcases:
            response = tester_create_activity(date_time=error_input)
            self.assertEqual(response.status_code, 400, response.json())

    def test_create_activity_with_empty_field(self):
        client = Client()
        tester_login(client=client)
        complete_data = {
            'title': "Second Activity",
            'datetime': now(),
            'location': "MSRA",
            'presenter': [{"id": User.objects.first().id}]
        }
        for missing_field in complete_data.keys():  # 四种数据各缺一遍。都不能成功创建
            incomplete_data = complete_data.copy()
            incomplete_data.pop(missing_field)
            response = client.post(activity_list_url, incomplete_data, content_type='application/json')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json().keys(), {missing_field})

        response = client.post(activity_list_url, complete_data, content_type='application/json')
        self.assertEqual(response.status_code, 201)  # 而正确数据是可以注册的

    def test_create_activity_with_invalid_field(self):
        correct_example = {
            'title': "Third Activity",
            'datetime': now(),
            'location': "MSRA",
            'presenter': [{"id": 1}]
        }

        field_and_invalid_example = [
            ['title', ''],
            ['datetime', ''],
            ['datetime', '2020-01-01'],
            ['datetime', '20:00'],
            ['datetime', '2021-02-29 20:00'],
            ['datetime', '2020-01-01 20:00+25:00'],
            ['datetime', '2020-01-01 20:00Y'],
            ['location', ''],
            ['presenter', [{}]],
            ['presenter', 'id:1'],
            ['presenter', [{"id": 233}]],
        ]
        self.assertEqual(Activity.objects.count(), 0)  # 没有创建活动
        client = Client()
        tester_login(client=client)
        for field, example in field_and_invalid_example:
            incorrect_example = correct_example.copy()
            incorrect_example[field] = example
            response = client.post(activity_list_url,
                                   data=incorrect_example,
                                   content_type='application/json')
            self.assertEqual(response.status_code, 400)  # 返回 400
            self.assertEqual(Activity.objects.count(), 0)  # 没有创建活动

    def test_get_activity_list(self):
        tester_create_activity('First Salon', now() - timedelta(weeks=1), 'MS Shanghai', [self.ids[0]])
        tester_create_activity('Second Salon', now() - timedelta(days=1), 'MS Beijing', [self.ids[2]])
        tester_create_activity('Third Salon', now() - timedelta(hours=2), 'MS Suzhou', [self.ids[3]])
        tester_create_activity('Fourth Salon', now(), 'MS Seattle', self.ids[0:3])

        client = Client()
        response = client.get(activity_list_url)
        self.assertEqual(response.status_code, 200)  # 未登录，get 返回 200

        tester_login(client=client)
        response = client.get(activity_list_url)
        self.assertEqual(response.status_code, 200)
        json_content = response.json()
        self.assertEqual(json_content['count'], 4)  # 总数正确
        results = json_content['results']
        self.check_order(results)  # 检查是否按日期降序排序

        for activity_dict in results:  # 检查每一个活动
            activity = Activity.objects.get(id=activity_dict['id'])
            assertActivityDetailEqual(self, activity_dict, activity)

    def test_search(self):
        # 定义验证返回结果的函数
        def check_search_queryset(_results: List[Dict], keywords: str):
            self.check_order(_results)
            results_id = list(map(lambda a: str(a['id']), _results))
            for a in Activity.objects.all():  # 检查 user 是否应当出现在搜索结果中，结果是否和预期相同
                presenter_names = a.presenter.all().values_list('first_name')[0]
                dt = a.datetime.isoformat()
                self.assertEqual(str(a.id) in results_id,
                                 keywords in f"{a.title} {dt} {a.location} {''.join(presenter_names)}",
                                 "keywords=%s\t"
                                 "title=%s\t"
                                 "datetime=%s\t"
                                 "locations=%s\t"
                                 "presenters=%s" % (keywords, a.title, dt, a.location, ''.join(presenter_names)))

        for i in range(0, 40):
            u = User(username="user%d@example.com" % (i + 1), first_name="user%d" % (i + 78))
            up = UserProfile(user=u, student_id=str(i + 37), about="你好，世界！", experience=randrange(1, 1000))
            u.save()
            up.save()
        self.assertEqual(User.objects.count(), 44)  # 最开始创建了 4 个用户
        for i in range(0, 40):
            a = Activity.objects.create(title=str(i + 55), location=str(i), datetime=now())
            a.presenter.add(User.objects.all()[i])
            a.save()

        client = Client()
        tester_login(client=client)
        test_keywords = range(10, 30)  # 测试的关键字
        for keyword in test_keywords:
            keyword = str(keyword)
            response = client.get("%s?search=%s&page_size=100" % (activity_list_url, keyword))  # page_size = 0 表示不分页
            self.assertEqual(response.status_code, 200)
            json_content = response.json()
            results = json_content['results']
            check_search_queryset(results, keyword)

        r1 = client.get("%s?search=&page_size=100" % activity_list_url)
        r2 = client.get("%s?page_size=100" % activity_list_url)
        self.assertEqual(json.loads(r1.content), json.loads(r2.content))  # search=<null> 应当不进行搜索

        r1 = client.get("%s?search=qwertyuiop&page_size=100" % activity_list_url)
        self.assertEqual(r1.status_code, 200)  # 搜索无结果，返回 200
        self.assertEqual(json.loads(r1.content)["results"], [])  # 搜索无结果，返回 results=[]

    def test_pagination(self):
        total_activities = 56
        for i in range(0, total_activities):
            Activity.objects.create(title=str(i + 55), location=str(i), datetime=now())
        self.assertEqual(Activity.objects.count(), total_activities)

        client = Client()
        tester_login(client=client)
        for page_size in [1, 2, 3, 5, 8, 13, 21, 34]:  # 计算这样分页的总页数和页大小
            total_pages = ceil(total_activities / page_size)
            for page in range(1, total_pages):
                r1 = client.get("%s?search=&page_size=%s&page=%s" % (activity_list_url, page_size, page))
                results1 = json.loads(r1.content)['results']
                count = json.loads(r1.content)['count']
                self.assertEqual(len(results1), page_size)  # 页大小正确
                self.assertEqual(count, total_activities)  # 页数正确
                self.check_order(results1)  # 结果顺序正确
                r2 = client.get("%s?page=%s&page_size=%s" % (activity_list_url, page, page_size))
                results2 = json.loads(r2.content)['results']
                self.assertEqual(results1, results2)  # 请求参数顺序不同，但结果相同
                # 判定 page_size 不合法时结果是否和默认 page_size 相同
                if page_size == Pagination.page_size:
                    for invalid_page_size in [-1, total_activities, 0, 'qwerty']:
                        r3 = client.get("%s?&page_size=%s&" % (activity_list_url, invalid_page_size))
                        self.assertEqual(r1.status_code, 200)
                        self.assertEqual(json.loads(r1.content), json.loads(r3.content))
            # 判定最后一页的正确性
            r1 = client.get("%s?&page_size=%s&=%s" % (activity_list_url, page_size, total_pages))
            results1 = json.loads(r1.content)['results']
            self.assertEqual(len(results1), page_size)  # 页大小正确
            self.check_order(results1)  # 结果顺序正确
            # 判定 page 不合法时结果的正确性
            for page in [-1, total_pages + 1, 0, 'qwerty']:
                r1 = client.get("%s?&page_size=%s&page=%s" % (activity_list_url, page_size, page))
                self.assertEqual(r1.status_code, 404, f"page={page}, page_size={page_size}")


class ActivityDetailTest(TestCase):
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

        tester_create_activity('First Salon', '2020-01-01T00:00:00.000Z', 'MS Shanghai', self.ids[0:2])
        tester_create_activity('Second Salon', '2021-01-01T00:00', 'MS Beijing', [self.ids[2]])
        tester_create_activity('Third Salon', '2021-02-01 00:00', 'MS Suzhou', [self.ids[3]])
        Activity.objects.create(title='Fourth Salon',
                                datetime='2021-02-28 08:00+08:00',
                                location='MS Seattle')
        Activity.objects.get(title='Fourth Salon').presenter.add(*list(User.objects.all()))
        self.assertEqual(Activity.objects.count(), 4)

    def test_get(self):
        client = Client()
        first_id = Activity.objects.first().id
        response = client.get(activity_detail_url(first_id))
        self.assertEqual(response.status_code, 200)  # 未登录用户访问，返回 200

        tester_login(client=client)
        for a in Activity.objects.all():
            response = client.get(activity_detail_url(a.id))
            assertActivityDetailEqual(self, response.content, a)

    def test_get_404(self):
        client = Client()
        for user_id in self.ids:
            client.force_login(User.objects.get(id=user_id))
            response = client.get(activity_detail_url(23333))
            self.assertEqual(response.status_code, 404)

    # 只测试 patch
    def test_patch_unauthorized(self):
        response = tester_create_activity(presenter_ids=[self.presenter.id, self.another_presenter.id])
        activity_id = response.json()['id']

        user_permissions = [  # 以六种用户身份去遍历
            [AnonymousUser, False],
            [self.superuser, True],
            [self.admin, True],
            [self.simple_user, False],
            [self.presenter, True],
            [self.another_presenter, True]
        ]

        for user, permission in user_permissions:
            new_title = Activity.objects.get(id=activity_id).title + '1'
            client = Client()
            if user != AnonymousUser:
                client.force_login(user)

            response = client.patch(activity_detail_url(activity_id),
                                    data={"title": new_title},
                                    content_type='application/json')
            self.assertEqual(response.status_code == 200, permission,
                             f"user={user}, status_code={response.status_code}")
            activity_title = Activity.objects.get(id=activity_id).title
            self.assertEqual(new_title == activity_title, permission,
                             f"user={user}, new_title={new_title}, current={activity_title}")

    def test_patch_404(self):
        client = Client()
        for user_id in self.ids:
            client.force_login(User.objects.get(id=user_id))
            response = client.patch(activity_detail_url(23333))
            self.assertEqual(response.status_code, 404)

    def test_patch_correctly(self):
        field_and_example = {
            "check_in_open": False,
            "presenter": [{"id": User.objects.filter(first_name="user")[0].id}],
            "location": "微软学生俱乐部",
            "datetime": "2021-01-01T20:00:00+08:00",
            "title": "中文沙龙"
        }

        client = Client()
        client.force_login(self.superuser)
        id = Activity.objects.first().id

        response = client.get(activity_detail_url(id))
        last_json = response.json()

        for field, example in field_and_example.items():
            response = client.patch(activity_detail_url(id),
                                    data={field: example},
                                    content_type='application/json')
            self.assertEqual(response.status_code, 200)
            last_json[field] = example
            activity = Activity.objects.first()
            assertActivityDetailEqual(self, last_json, activity)  # 比较更新后数据库和预期值

    def test_patch_with_invalid_value(self):
        field_and_invalid_example = [
            ['title', ''],
            ['datetime', ''],
            ['datetime', '2020-01-01'],
            ['datetime', '20:00'],
            ['datetime', '2021-02-29 20:00'],
            ['datetime', '2020-01-01 20:00+25:00'],
            ['datetime', '2020-01-01 20:00Y'],
            ['location', ''],
            ['presenter', [{}]],
            ['presenter', 'id:1'],
            ['presenter', [{"id": 233}]],
            ['check_in_open', 2333],
        ]

        client = Client()
        client.force_login(self.superuser)
        id = Activity.objects.first().id

        for field, example in field_and_invalid_example:
            response = client.patch(activity_detail_url(id),
                                    data={field: example},
                                    content_type='application/json')
            self.assertEqual(response.status_code, 400, f"{field}={example}")  # 返回 400
            response = client.get(activity_detail_url(id))
            json_response = response.json()
            self.assertNotEqual(json_response[field], example)  # GET 的数据并没有被修改

    # 删除就懒得写测试了
    def test_delete_activity(self):
        pass


class ActivityLinkTest(TestCase):
    pass


class ActivityDetailAdmin(TestCase):
    def setUp(self):
        # 设置用户的权限
        self.superuser = User.objects.create_user(username="superuser@aka.ms", first_name="superuser",
                                                  is_superuser=True)
        self.admin = User.objects.create_user(username="admin@aka.ms", first_name="admin", is_staff=True)
        self.simple_user = User.objects.create_user(username="a_user@aka.ms", first_name="user")
        self.presenter = User.objects.create_user(username="presenter@aka.ms", first_name="presenter")
        self.another_presenter = User.objects.create_user(username="another_presenter@aka.ms",
                                                          first_name="another_presenter")

        response = tester_create_activity(presenter_ids=[self.presenter.id, self.another_presenter.id])
        self.activity_id = response.json()['id']

    def test_get_unauthorized(self):
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

            response = client.get(activity_detail_admin_url(self.activity_id))
            self.assertEqual(response.status_code == 200, permission,
                             f"user={user}, status_code={response.status_code}")
            if permission:
                self.assertEqual(response.json()['check_in_code'],
                                 Activity.objects.first().check_in_code)

    def test_404(self):
        client = Client()
        for user in [self.superuser, self.admin, self.simple_user, self.presenter, self.another_presenter]:
            client.force_login(user)
            response = client.get(activity_detail_admin_url(23333))
            self.assertEqual(response.status_code, 404)


class ActivityCheckInTest(TestCase):
    def setUp(self):
        tester_signup()
        tester_signup("superuser@example.com", "supersuper", "superuser", "1297391")
        tester_signup("user@example.com", "useruser", "user", "1297392")
        tester_signup("anotheruser@example.com", "anotheruser", "anotheruser", "1297393")
        self.superuser = User.objects.filter(first_name="superuser")[0]
        self.superuser.is_superuser = True
        self.superuser.save()
        self.admin = User.objects.filter(first_name="admin")[0]
        self.admin.is_admin = True
        self.admin.save()
        self.user = User.objects.filter(first_name="user")[0]
        self.another_user = User.objects.filter(first_name="anotheruser")[0]

        tester_create_activity('First Salon', '2020-01-02T20:00+08:00', 'MS Shanghai', [self.user.id])
        self.activity = Activity.objects.first()
        self.second_activity = Activity.objects.create(title='Second Salon',
                                                       datetime='2021-02-28 08:00+08:00',
                                                       location='MS Seattle')
        Activity.objects.get(title='Second Salon').presenter.add(*list(User.objects.all()))

        self.assertEqual(Activity.objects.count(), 2)

    @mock.patch('activities.views.now')
    def test_check_in_correctly(self, mocked_now):
        mocked_now.return_value = datetime(2020, 1, 2, 20, 15,
                                           tzinfo=pytz.timezone('Asia/Shanghai'))  # 通过 mock 重新定义 view.now()
        self.activity.refresh_from_db()
        self.assertEqual(self.activity.attender.count(), 0)

        users = [self.superuser, self.admin, self.user, self.another_user]
        for i in range(len(users)):
            user = users[i]
            client = Client()
            client.force_login(user)
            response = client.post(activity_check_in_url(self.activity.id), {
                "check_in_code": self.activity.check_in_code
            })
            self.assertEqual(response.status_code, 200)  # 签到成功
            self.activity.refresh_from_db()
            self.assertEqual(self.activity.attender.count(), i + 1)  # 活动参与人数 + 1

        self.second_activity.refresh_from_db()
        self.assertEqual(self.second_activity.attender.count(), 0)  # 另一场活动的人数没有变化

    @mock.patch('activities.views.now')
    def test_check_in_unauthorized(self, mocked_now):
        mocked_now.return_value = datetime(2020, 1, 2, 20, 15, tzinfo=pytz.timezone('Asia/Shanghai'))
        response = Client().post(activity_check_in_url(self.activity.id), {
            "check_in_code": self.activity.check_in_code
        })
        self.assertEqual(response.status_code, 403)
        self.activity.refresh_from_db()
        self.assertEqual(self.activity.attender.count(), 0)

    @mock.patch('activities.views.now')
    def test_check_in_with_empty_field(self, mocked_now):
        mocked_now.return_value = datetime(2020, 1, 2, 20, 15, tzinfo=pytz.timezone('Asia/Shanghai'))
        client = Client()
        client.force_login(self.user)
        response = client.post(activity_check_in_url(self.activity.id))
        self.assertEqual(response.status_code, 400)  # 没提交签到码，签到失败
        self.activity.refresh_from_db()
        self.assertEqual(self.activity.attender.count(), 0)

    @mock.patch('activities.views.now')
    def test_check_in_with_invalid_field(self, mocked_now):
        mocked_now.return_value = datetime(2020, 1, 2, 20, 15, tzinfo=pytz.timezone('Asia/Shanghai'))
        code = self.activity.check_in_code
        invalid_examples = ['', '12345', 'QAQAQ', code + ' ', code + 'Q', code[0:-1]]
        client = Client()
        client.force_login(self.user)
        for example in invalid_examples:
            response = client.post(activity_check_in_url(self.activity.id), {
                "check_in_code": invalid_examples
            })
            self.assertEqual(response.status_code, 403)  # 签到码错误，签到失败
            self.activity.refresh_from_db()
            self.assertEqual(self.activity.attender.count(), 0)

    @mock.patch('activities.views.now')
    def test_check_in_404(self, mocked_now):
        mocked_now.return_value = datetime(2020, 1, 2, 20, 15, tzinfo=pytz.timezone('Asia/Shanghai'))
        client = Client()
        client.force_login(self.user)
        response = client.post(activity_check_in_url(2333), {
            "check_in_code": self.activity.check_in_code
        })
        self.assertEqual(response.status_code, 404)  # 活动不存在，签到失败

    @mock.patch('activities.views.now')
    def test_check_in_anytime(self, mocked_now):
        for day in [1, 2, 3]:
            is_today = day == 2
            for hour in range(24):
                mocked_now.return_value = datetime(2020, 1, day, hour, 15, tzinfo=pytz.timezone('Asia/Shanghai'))
                client = Client()
                client.force_login(self.user)
                response = client.post(activity_check_in_url(self.activity.id), {
                    "check_in_code": self.activity.check_in_code
                })
                self.assertEqual(response.status_code, 200 if is_today else 403, f'date={mocked_now.return_value}')
                self.activity.refresh_from_db()
                self.assertEqual(self.activity.attender.count(), 1 if is_today else 0)
                self.activity.attender.clear()

    @mock.patch('activities.views.now')
    def test_check_in_activity_that_closes_check_in(self, mocked_now):
        mocked_now.return_value = datetime(2020, 1, 2, 20, 15, tzinfo=pytz.timezone('Asia/Shanghai'))
        for check_in_open in [True, False, True, False, True]:
            self.activity.check_in_open = check_in_open
            self.activity.attender.clear()
            self.activity.save()
            client = Client()
            client.force_login(self.user)
            response = client.post(activity_check_in_url(self.activity.id), {
                "check_in_code": self.activity.check_in_code
            })
            self.assertEqual(response.status_code, 200 if check_in_open else 403)
            self.activity.refresh_from_db()
            self.assertEqual(self.activity.attender.count(), 1 if check_in_open else 0)
            self.activity.attender.clear()


class ActivityCheckInAdminTest(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_user(id=1, username="superuser@example.com", password="supersuper",
                                                  is_superuser=True)
        self.admin = User.objects.create_user(id=2, username="admin@example.com", password="adminadmin", is_staff=True)
        self.user = User.objects.create_user(id=3, username="user@example.com", password="useruser")
        self.another_user = User.objects.create_user(id=4, username="anotheruser@example.com", password="anotheruser")

        tester_create_activity('First Salon', '2020-01-02T20:00+08:00', 'MS Shanghai', [self.user.id])
        self.activity = Activity.objects.first()
        self.assertEqual(Activity.objects.count(), 1)

    def test_admin_check_in_correctly(self):
        input_and_result = [
            [{"add": [1, 2, 3]}, {1, 2, 3}],
            [{"remove": [1, 3]}, {2}],
            [{"add": [4], "remove": [2]}, {4}]
        ]
        client = Client()
        client.force_login(self.superuser)
        self.activity.refresh_from_db()
        self.assertEqual(self.activity.attender.count(), 0)

        for post_data, expected in input_and_result:
            response = client.patch(activity_detail_admin_check_in_url(self.activity.id), post_data,
                                    content_type='application/json')
            self.assertEqual(response.status_code, 200)
            self.activity.refresh_from_db()
            attender_list = list(self.activity.attender.all())
            attender_set = set(map(lambda u: u.id, attender_list))
            self.assertSetEqual(expected, attender_set)

    def test_admin_check_in_unauthorized(self):

        user_permissions = [  # 以六种用户身份去遍历
            [AnonymousUser, False],
            [self.superuser, True],
            [self.admin, True],
            [self.user, True],
            [self.another_user, False]
        ]

        for user, permission in user_permissions:
            client = Client()
            if user != AnonymousUser:
                client.force_login(user)

            response = client.patch(activity_detail_admin_check_in_url(self.activity.id), data={"add": [1]},
                                    content_type='application/json')
            self.assertEqual(response.status_code == 200, permission,
                             f"user={user.username}, status_code={response.status_code}")
            self.assertEqual(self.activity.attender.count() == 1, permission, f"user={user}")

            self.activity.attender.clear()

    def test_admin_check_in_with_empty_field(self):
        client = Client()
        client.force_login(self.superuser)
        response = client.patch(activity_detail_admin_check_in_url(self.activity.id), {"add": []},
                                content_type='application/json')
        self.assertEqual(response.status_code, 200)  # 没有为用户签到，但是执行成功了

    def test_admin_check_in_with_invalid_field(self):
        client = Client()
        client.force_login(self.superuser)
        response = client.patch(activity_detail_admin_check_in_url(self.activity.id), {"add": [1], "remove": [2333]},
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)     # 若 add 或 remove 有错误，整个请求不应该被执行
        self.assertEqual(self.activity.attender.count(), 0)

    def test_admin_check_in_404(self):
        client = Client()
        client.force_login(self.superuser)
        response = client.patch(activity_detail_admin_check_in_url(233), {"add": [1, 2, 3]},
                                content_type='application/json')
        self.assertEqual(response.status_code, 404)  # 活动不存在，签到失败
