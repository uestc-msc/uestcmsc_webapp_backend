import asyncio
import functools
import threading
from typing import Callable


from asgiref.sync import sync_to_async


def run_in_new_thread(func: Callable):
    """
    装饰器，用于在新线程执行函数（如发送邮件），且函数不会阻塞主线程
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        runner = threading.Thread(target=func, args=args, kwargs=kwargs)
        runner.start()
    return wrapper


def thread_insensitive_sync_to_async(func: Callable):
    """
    装饰器，类似于 sync_to_async 的用法，但是返回的函数是线程不敏感的（thread_sensitive=False）
    语法上，该装饰器将同步函数转为异步函数
    装饰后的函数将在一个新的线程上执行，不会阻塞主线程
    注：该装饰器目前不能用于 Django Rest Framework 视图
    """
    return sync_to_async(func, thread_sensitive=False)
