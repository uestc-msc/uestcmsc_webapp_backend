from datetime import datetime
from typing import List

from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed, Enclosure

from activities.models import Activity
from cloud.models import OnedriveFile
from config import FRONTEND_URL


class ActivityFeed(Feed):
    feed_type = Atom1Feed
    title = "UESTC-MSC 近期沙龙"
    link = FRONTEND_URL + '/activity/'
    subtitle = "电子科技大学微软学生俱乐部的近期活动"
    author_name = "电子科技大学微软学生俱乐部"
    author_email = "uestcmsc@demo4c.onmicrosoft.com"
    author_link = "https://uestc-msc.github.io/"
    feed_url = '/api/feed'

    def items(self):
        return Activity.objects.order_by('-datetime')[:10]

    def item_title(self, item: Activity) -> str:
        return item.title

    def item_description(self, item: Activity) -> str:
        return f"地点：{item.location}"

    def item_link(self, item: Activity) -> str:
        return FRONTEND_URL + f'/activity/{item.id}'

    def item_author_name(self, item: Activity) -> str:
        presenters = item.presenter.all()
        return '、'.join([u.first_name for u in presenters])

    # 附件
    def item_enclosures(self, item: Activity) -> List[Enclosure]:
        def make_enclosure(file: OnedriveFile) -> Enclosure:
            return Enclosure(file.download_link, str(file.size), file.mimetype)
        photos = item.photo.all()
        files = item.file.all()
        return [make_enclosure(f) for f in photos] + [make_enclosure(f) for f in files]

    def item_pubdate(self, item: Activity) -> datetime:
        return item.datetime