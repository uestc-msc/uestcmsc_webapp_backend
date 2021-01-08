from rest_framework import permissions, routers
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from config import API_VERSION, APP_NAME

# API 文档页
schema_view = get_schema_view(
   openapi.Info(
      title=APP_NAME+" 后端",
      default_version=API_VERSION,
      description=r"https://github.com/uestc-msc/uestcmsc_webapp_backend",
      # terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="uestcmsc@demo4c.onmicrosoft.com"),
      license=openapi.License(name="MIT License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)