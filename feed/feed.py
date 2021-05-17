from django.contrib.syndication.views import Feed
from activities.models import Activity
from config import FRONTEND_URL


class ActivityFeed(Feed):
    title = "UESTC-MSC 近期沙龙"
    link = FRONTEND_URL + '/activity/'
    description = "电子科技大学微软学生俱乐部的近期活动"

    def items(self):
        return Activity.objects.order_by('-datetime')[:5]

    def item_title(self, item: Activity) -> str:
        return item.title

    def item_description(self, item: Activity) -> str:
        time = item.datetime.strftime('%d 月 %Y 日 %H:%M')
        presenters = item.presenter.all()
        presenter_list = '、'.join(map(lambda u: u.first_name, presenters))
        return f"时间：{time}\n" \
               f"地点：{item.location}\n" \
               f"主讲人：{presenter_list}"

    def item_link(self, item: Activity) -> str:
        return FRONTEND_URL + f'/activity/{item.id}'