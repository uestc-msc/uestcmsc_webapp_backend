from smtplib import SMTPException

from django.core.mail import send_mail

from config import *
from uestcmsc_webapp_backend.settings import APP_NAME
from utils.asynchronous import asynchronous
from utils.log import log_error, log_info


@asynchronous
def send_reset_password_email(receipt_email: str, name: str, token: str):
    """
    发送重置密码的邮件，成功后返回 True
    参考文档：https://docs.djangoproject.com/zh-hans/3.1/topics/email/
    测试参考文档：https://docs.djangoproject.com/zh-hans/3.1/topics/testing/tools/#topics-testing-email
    """
    message = f"亲爱的 {name}：\n\n" \
              f"您似乎忘记了您在“阮薇薇签到啦”的密码。您可以点击以下链接（或粘贴到浏览器访问）来重置您的密码：\n\n" \
              f"{FRONTEND_URL}/resetpassword?token={token}\n\n" \
              f"该链接 24 小时内有效。\n" \
              f"如果这不是您的请求，不用担心，您的个人信息并没有泄露。\n\n" \
              f"电子科技大学微软学生俱乐部"

    try:
        send_mail(
            subject=f"[{APP_NAME}] 重设您的密码",
            message=message,
            from_email=MAILBOX_EMAIL,
            recipient_list=[receipt_email],
            fail_silently=False)
        log_info(f"向 {name} ({receipt_email}) 发送邮件成功")
    except SMTPException as e:
        log_error(f"向 {name} ({receipt_email}) 发送邮件失败：{e}")
