from rest_framework.generics import get_object_or_404

from activities.models import Activity
from activities_files.models import ActivityFolder
from utils.onedrive import app_root


# 获取某活动的文件夹。如果不存在，则创建
def get_or_create_activity_folder(activity_id: int) -> ActivityFolder:
    onedrive_folder = ActivityFolder.objects.filter(activity_id=activity_id)
    if not onedrive_folder:
        # 文件夹不存在，需要创建
        activity = get_object_or_404(Activity, id=activity_id)
        activity_date = activity.datetime.strftime("%Y%m%d")
        # 按 “日期 标题”的格式创建沙龙文件夹
        response = app_root.create_directory_recursive(f'/沙龙/{activity_date} {activity.title}')
        onedrive_folder = ActivityFolder.objects.create(activity_id=activity_id, id=response.json().id)
    return onedrive_folder
