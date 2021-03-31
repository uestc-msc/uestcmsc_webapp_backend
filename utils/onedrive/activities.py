from rest_framework.generics import get_object_or_404

from activities.models import Activity
from activities_files.models import ActivityOnedriveFolder
from utils.onedrive import app_root


def get_or_create_activity_folder(activity_id: int) -> ActivityOnedriveFolder:
    onedrive_folder = ActivityOnedriveFolder.objects.filter(activity_id=activity_id)
    if not onedrive_folder:
        # 文件夹不存在，需要创建
        activity = get_object_or_404(Activity, id=activity_id)
        activity_date = activity.datetime.strftime("%Y%m%d")
        # 按 “日期 标题”的格式创建沙龙文件夹
        response = app_root.create_directory_recursive(f'/沙龙/{activity_date} {activity.title}')
        onedrive_folder = ActivityOnedriveFolder.objects.create(activity_id=activity_id, id=response.json().id)
    return onedrive_folder
