from django.contrib.auth import authenticate
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters
from rest_framework.decorators import api_view
from rest_framework.generics import *
from rest_framework.request import Request

from utils import Pagination
from utils.permissions import *
from utils.swagger import *
from utils.validators import is_email, is_valid_password
from .serializer import UserSerializer


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_summary='获取用户列表',
    operation_description='获取用户列表（以及总页数），可对姓名、邮箱、学号进行搜索，并可指定页码和每页大小\n'
                          '数据作为 list 返回在 `results` 中，返回值的 `count` 为搜索结果的总数\n'
                          '考虑到数据安全，非管理员获取该列表的结果中，所有人的学号会被替换为学号前四位，邮箱会被替换为 `***`\n'
                          '返回结果以经验值降序排序\n'
                          '注 1：如页码不正确或不存在，返回 404\n'
                          '注 2：如每页大小不正确或不存在，使用默认每页大小（15）\n'
                          '注 3：如无搜索结果，返回 200，其中 `results` 为空',
    manual_parameters=[Param_search, Param_page, Param_page_size],
))
class UserListView(ListAPIView):
    queryset = User.objects.all().order_by("-userprofile__experience")
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username', 'first_name', 'last_name', 'userprofile__student_id')
    pagination_class = Pagination
    serializer_class = UserSerializer


@method_decorator(name="get", decorator=swagger_auto_schema(
    operation_summary='获取用户信息',
    operation_description='获取一个的用户信息，成功返回 200\n'
                          # '注：需要登录，否则返回 403',
))
@method_decorator(name="put", decorator=swagger_auto_schema(
    operation_summary='更新用户信息',
    operation_description='响应报文和 PATCH 方法相同，但 PUT 要求在请求中提交所有信息',
    ))
@method_decorator(name="patch", decorator=swagger_auto_schema(
    operation_summary='更新用户部分信息',
    operation_description='更新一个用户的信息，成功返回 200\n'
                          '如用户不存在，返回 404\n'
                          '如更新的参数有错误，返回 400\n'
                          '注：需要是用户本人或管理员，否则返回 403\n'
                          '注：PATCH 方法可以只提交更新的值，也可以提交所有值'
))
@method_decorator(name="delete", decorator=swagger_auto_schema(
    operation_summary='删除用户',
    operation_description='删除用户，成功返回 204\n'
                          '如用户不存在，返回 404\n'
                          '注：需要是用户本人或管理员，否则返回 403'
))
class UserDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsSelfOrAdminOrReadOnly, )
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'


@swagger_auto_schema(
    method='PATCH',
    operation_summary='修改密码',
    operation_description='修改邮箱和密码，用户需要满足以下两个条件之一：\n'
                          '1. 修改本人的邮箱密码，且需要提供旧密码 old_password\n'
                          '2. 管理员或超级用户修改权限比自己低的用户的邮箱密码，无需提供旧密码\n\n'
                          '若 id 不正确，返回 404\n'
                          '若无权修改（不满足以上两个条件），返回 403\n'
                          '若 new_password 不合法，返回 400 `{"detail": "新密码不合法"}`\n'
                          '若 new_email 不合法或已存在，返回 400 `{"detail": "新邮箱不合法或已存在"}`\n'
                          '验证正确性后，修改邮箱及密码，返回 204\n'
                          '注 1：new_email 和 new_password 可以不同时存在\n'
                          '注 2：若 new_email 和 new_password 其中一项错误，对另一项的修改也不会生效\n'
                          '注 3：修改密码会使得已有的登录失效',
    request_body=Schema_object(Schema_old_password, Schema_new_email, Schema_new_password),
    responses={200: Schema_None}
)
@api_view(['PATCH'])
@login_required
def change_password_view(request: Request, id: int) -> Response:
    user2 = get_object_or_404(User, id=id)
    # 权限判定
    if not hasGreaterPermissions(request.user, user2):
        if not (request.user.is_authenticated
                and "old_password" in request.data
                and authenticate(request, username=request.user.username, password=request.data["old_password"])):
            return Response(status=status.HTTP_403_FORBIDDEN)
    # 对更新数据的判定
    new_email = request.data.pop('new_email', None)
    new_password = request.data.pop('new_password', None)
    if new_email and \
            (not is_email(new_email) or User.objects.filter(username=new_email)):
        return Response({"detail": "新邮箱不合法或已存在"}, status=status.HTTP_400_BAD_REQUEST)
    if new_password and not is_valid_password(new_password):
        return Response({"detail": "新密码不合法"}, status=status.HTTP_400_BAD_REQUEST)
    # 更新数据
    if new_email:
        request.user.username = new_email
    if new_password:
        request.user.set_password(new_password)
    request.user.save()
    return Response(status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(
    method='GET',
    operation_summary='获取用户自身信息',
    operation_description='获取用户自身的信息，成功返回 200，响应报文和 `/users/<id>` 成功的响应报文相同\n'
                          '注：需要登录（即 Headers 中包含 Cookies: `sessionid: xxxx`），否则返回 403\n',
    responses={200: UserSerializer()}
)
@api_view(['GET'])
def whoami_view(request: Request) -> Response:
    if not request.user.is_authenticated:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    else:
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
