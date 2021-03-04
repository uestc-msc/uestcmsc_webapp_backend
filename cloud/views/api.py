from django.core.cache import cache
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import redirect
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from utils.swagger import *
from utils.onedrive.auth import OnedriveAuthentication, onedrive_access_token_cache_name, \
    onedrive_refresh_token_cache_name
from config import FRONTEND_URL


def onedrive_create_upload_session(request: WSGIRequest) -> Response:
    pass


def onedrive_upload_done(request: WSGIRequest) -> Response:
    pass