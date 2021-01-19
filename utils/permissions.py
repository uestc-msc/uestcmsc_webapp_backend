from functools import wraps
from typing import Callable

from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest
from rest_framework import status
from rest_framework.response import Response


def isOwnerOrAdmin(request: WSGIRequest, owner: User):
    return request.user.is_staff or request.user.is_superuser or request.user == owner


# 一系列装饰器
def __user_passes_test(test_func):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(*args, **kwargs) -> Response:
            # args[0] may be 'self' (for Class Based View) or request(for Function Based View)
            if hasattr(args[0], 'user'):
                request = args[0]
            else:
                assert hasattr(args[1], 'user')
                request = args[1]
            if test_func(request.user):
                return view_func(*args, **kwargs)
            elif not request.user.is_authenticated:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response(status=status.HTTP_403_FORBIDDEN)
        return _wrapped_view
    return decorator


def login_required(function: Callable = None):
    actual_decorator = __user_passes_test(lambda u: u.is_authenticated)
    return actual_decorator(function)


def admin_required(function: Callable = None):
    actual_decorator = __user_passes_test(lambda u: u.is_authenticated and (u.is_staff or u.is_superuser))
    return actual_decorator(function)


def superuser_required(function: Callable = None):
    actual_decorator = __user_passes_test(lambda u: u.is_authenticated and u.is_superuser)
    return actual_decorator(function)

