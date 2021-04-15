from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from cloud.onedrive.api.auth import OnedriveAuthentication
from cloud.onedrive.api.cache import get_access_token, get_refresh_token
from utils.swagger import *


@swagger_auto_schema(
    method='GET',
    operation_summary='Onedrive 状态',
    operation_description='获取 Onedrive 状态，取值有三种：`login_required`, `active`, `error`',
    responses={200: Schema_object(Schema_status)}
)
@api_view(['GET'])
def onedrive_status(request: Request) -> Response:
    access_token_available = get_access_token() is not None
    refresh_token_available = get_refresh_token() is not None
    if refresh_token_available and not access_token_available:
        OnedriveAuthentication.refresh_access_token()
        access_token_available = get_access_token() is not None

    status_strings = [
        ['login_required', 'error: only access token'],    # refresh is False
        ['error: only refresh token', 'active']            # refresh is True
    ]
    current_status = status_strings[refresh_token_available][access_token_available]
    return Response({"status":current_status}, status=status.HTTP_200_OK)
