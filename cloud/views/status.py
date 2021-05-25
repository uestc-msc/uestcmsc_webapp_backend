from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from cloud.onedrive.api.auth import OnedriveAuthentication
from utils.cache import Cache
from utils.swagger import *


@swagger_auto_schema(
    method='GET',
    operation_summary='Onedrive 状态',
    operation_description='获取 Onedrive 状态，取值有三种：`login_required`, `active`, `error`',
    responses={200: Schema_object(Schema_status)}
)
@api_view(['GET'])
def onedrive_status_view(request: Request) -> Response:
    access_token_available = Cache.onedrive_access_token is not None
    refresh_token_available = Cache.onedrive_refresh_token is not None
    if refresh_token_available and not access_token_available:
        # 这种情况可能是 access_token 过期了，所以立即尝试获取 access_token
        OnedriveAuthentication.refresh_access_token()
        access_token_available = Cache.onedrive_access_token is not None

    status_strings = [
        ['login_required', 'error: only access token'],    # refresh is False
        ['error: only refresh token', 'active']            # refresh is True
    ]
    current_status = status_strings[refresh_token_available][access_token_available]
    return Response({"status":current_status}, status=status.HTTP_200_OK)
