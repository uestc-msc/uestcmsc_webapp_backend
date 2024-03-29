import re
from time import sleep

from rest_framework.generics import get_object_or_404

from activities.models import Activity
from activities_files.models import ActivityFolder
from cloud.onedrive import onedrive_approot
from cloud.onedrive.api import onedrive_business_reserved, onedrive_business_reserved_re


# 获取某活动的文件夹。如果不存在，则创建
def get_or_create_activity_folder(activity_id: int) -> ActivityFolder:
    onedrive_folder = ActivityFolder.objects.filter(activity_id=activity_id)
    if onedrive_folder:
        return onedrive_folder[0]
    else:
        # 文件夹不存在，需要创建
        activity = get_object_or_404(Activity, id=activity_id)
        activity_date = activity.datetime.strftime("%Y%m%d")
        # 去掉沙龙标题中的特殊符号
        activity_title = re.sub(onedrive_business_reserved_re, '_', activity.title)
        # 按 “日期_标题”的格式创建沙龙文件夹
        response = onedrive_approot.create_directory_recursive(f'/沙龙/{activity_date}_{activity_title}')
        if response.status_code == 409: # 出现 409，可能是并发请求导致几个会话都在创建文件夹，导致冲突
            sleep(1)
            return ActivityFolder.objects.filter(activity_id=activity_id)[0] # 如果不存在就抛 500 了
        return ActivityFolder.objects.create(activity_id=activity_id, id=response.json()['id'])
