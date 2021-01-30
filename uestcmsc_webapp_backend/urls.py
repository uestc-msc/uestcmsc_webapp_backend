"""uestcmsc_webapp_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url
from django.http import HttpResponse
from django.urls import path, include
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view

from .docs import schema_view
from .settings import API_VERSION


def hello_world(request):
    return HttpResponse("Hello UESTC-MSCer! This is the backend of UESTC-MSC Webapp.")


@swagger_auto_schema(
    method='GET',
    operation_summary='获取 API 版本号',
    operation_description=r'返回 `X.Y.Z`，遵循[语义化版本控制](https://semver.org/lang/zh-CN/)。'
)
@api_view(['GET'])
def version(request):
    return HttpResponse(API_VERSION)


api_urlpatterns = [
    url(r'^docs(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^docs/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('activities/', include('activities.urls')),
    path('users/', include('users.urls')),
    path('', hello_world),
    path('version/', version)
]

urlpatterns = [
    url('api/', include(api_urlpatterns))
]
