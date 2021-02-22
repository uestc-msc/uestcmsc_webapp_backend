from functools import wraps
from typing import Callable

from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest
from rest_framework import status
from rest_framework.permissions import *
from rest_framework.response import Response

from activities.models import Activity


def isOwnerOrAdmin(request: WSGIRequest, owner: User) -> bool:
    return request.user.is_staff or request.user.is_superuser or request.user == owner


# 判断 user1 的权限是否大于 user2
def hasGreaterPermissions(user1: User, user2: User) -> bool:
    def permission_value(user: User):
        if user.is_superuser:
            return 2
        elif user.is_staff:
            return 1
        else:
            return 0
    # superuser 拥有最高权限
    return user1.is_superuser or permission_value(user1) > permission_value(user2)


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


# 一系列 Django REST Framework 权限 (Permission)
class IsAuthenticatedOrPostOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.method in ('POST', 'OPTION') or
            request.user and
            request.user.is_authenticated
        )


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in SAFE_METHODS or
            request.user and
            obj.user == request.user
        )


class IsAdminOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in SAFE_METHODS or
            request.user and
            (request.user.is_staff or request.user.is_superuser)
        )


class IsSuperuserOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in SAFE_METHODS or
            request.user and
            request.user.is_superuser
        )


class IsOwnerOrAdminOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in SAFE_METHODS or
            request.user and
            (obj.user == request.user or request.user.is_staff or request.user.is_superuser)
        )


class IsPresenterOrAdmin(BasePermission):
    def has_object_permission(self, request, view, activity: Activity):
        return bool(
            request.user and
            (request.user in activity.presenter.all() or request.user.is_staff or request.user.is_superuser)
        )


class IsPresenterOrAdminOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, activity: Activity):
        return bool(
            request.method in SAFE_METHODS or
            request.user and
            (activity.presenter.filter(id=request.user.id) or request.user.is_staff or request.user.is_superuser)
        )


class IsSelfOrAdminOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, user: User):
        return bool(
            request.method in SAFE_METHODS or
            request.user and
            (user == request.user or request.user.is_staff or request.user.is_superuser)
        )
