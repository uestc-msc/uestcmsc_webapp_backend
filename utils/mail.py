import logging
from smtplib import SMTPException

from django.core.mail import send_mail, mail_admins

from config import *
from uestcmsc_webapp_backend.settings import APP_NAME
from utils.asynchronous import run_in_new_thread

logger = logging.getLogger(__name__)


@run_in_new_thread
def send_reset_password_email(receipt_email: str, name: str, token: str):
    """
    发送重置密码的邮件，成功后返回 True
    参考文档：https://docs.djangoproject.com/zh-hans/3.1/topics/email/
    测试参考文档：https://docs.djangoproject.com/zh-hans/3.1/topics/testing/tools/#topics-testing-email
    """
    message = f"亲爱的{name}：\n\n" \
              f"您似乎忘记了您在“{APP_NAME}”的密码。您可以点击以下链接（或粘贴到浏览器访问）来重置您的密码：\n\n" \
              f"{FRONTEND_URL}/resetpassword?token={token}\n\n" \
              f"该链接 24 小时内有效。\n" \
              f"如果这不是您的请求，不用担心，您的个人信息并没有泄露。\n\n" \
              f"电子科技大学微软学生俱乐部"

    try:
        send_mail(subject=f"[{APP_NAME}] 重设您的密码",
                  message=message,
                  from_email=MAILBOX_EMAIL,
                  recipient_list=[receipt_email],
                  fail_silently=False)
        logger.info(f"向 {name} ({receipt_email}) 发送邮件成功")
    except SMTPException as e:
        logger.error(f"向 {name} ({receipt_email}) 发送邮件失败：{e}")


@run_in_new_thread
def send_system_alert_mail_to_managers(info: str):
    message = f"{APP_NAME}管理员：\n" \
              f"{APP_NAME}出现异常情况，详情如下：\n\n" \
              f"{info}\n" \
              f"" \
              f"请及时处理。感谢您对{APP_NAME}的维护！\n" \
              f"电子科技大学微软学生俱乐部"
    try:
        mail_admins(subject=f"[{APP_NAME}] 系统警告", message=message, fail_silently=True)
        logger.info(f"向 MANAGERS（共 {len(MANAGERS)} 人）发送邮件")
    except SMTPException as e:
        logger.error(f"向 MANAGERS 发送邮件失败：{e}")
