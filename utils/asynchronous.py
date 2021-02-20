import functools
import threading
from typing import Callable


# 用于异步执行函数（如发送邮件）的装饰器。装饰后的函数无返回值
def asynchronous(func: Callable):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        runner = threading.Thread(target=func, args=args, kwargs=kwargs)
        runner.start()
    return wrapper
