from functools import wraps
from typing import Callable

from django.core.handlers.wsgi import WSGIRequest
from rest_framework import status
from rest_framework.response import Response


def __user_passes_test(test_func):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request: WSGIRequest, *args, **kwargs) -> Response:
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            elif not request.user.is_authenticated:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response(status=status.HTTP_403_FORBIDDEN)
        return _wrapped_view
    return decorator


def login_required(function: Callable = None):
    """
    Decorator for views that checks that the user is logged in,
    or raise HTTP 401
    """
    actual_decorator = __user_passes_test(
        lambda u: u.is_authenticated
    )
    if function is not None:
        return actual_decorator(function)
    return actual_decorator


def admin_required(function: Callable = None):
    """
    Decorator for views that checks that the user is admin or superuser,
    otherwise raise HTTP 401 for anonymous users or HTTP 403 for other users
    """
    actual_decorator = __user_passes_test(
        lambda u: u.is_authenticated and (u.is_staff or u.is_superuser)
    )
    if function is not None:
        return actual_decorator(function)
    return actual_decorator


def superuser_required(function: Callable = None):
    """
    Decorator for views that checks that the user is superuser,
    otherwise raise HTTP 401 for anonymous users or HTTP 403 for other users
    """
    actual_decorator = __user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser
    )
    if function is not None:
        return actual_decorator(function)
    return actual_decorator
