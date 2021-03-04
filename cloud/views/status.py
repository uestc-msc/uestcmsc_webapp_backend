from django.core.cache import cache
from django.core.handlers.wsgi import WSGIRequest
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from utils.onedrive.auth import onedrive_access_token_cache_name, \
    onedrive_refresh_token_cache_name
from utils.swagger import *


@swagger_auto_schema(
    method='GET',
    operation_summary='Onedrive 状态',
    operation_description='获取 Onedrive 状态，取值有三种：`login_required`, `active`, `error`, `refreshing`',
    responses={200: Schema_object(Schema_status)}
)
@api_view(['GET'])
def onedrive_status(request: WSGIRequest) -> Response:
    access_token_available = cache.get(onedrive_access_token_cache_name, '') != ''
    refresh_token_available = cache.get(onedrive_refresh_token_cache_name, '') != ''
    status_strings = [
        ['login_required', 'error'],    # refresh is False
        ['refreshing', 'active']        # refresh is True
    ]
    current_status = status_strings[refresh_token_available][access_token_available]
    return Response({"status":current_status}, status=status.HTTP_200_OK)
