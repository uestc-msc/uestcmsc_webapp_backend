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
                          '注：非管理员获取非本人信息时，邮箱会被替换为 `***`，学号会被替换为入学年份'
))
@method_decorator(name="put", decorator=swagger_auto_schema(
    operation_summary='更新用户信息',
    operation_description='应答和 PATCH 方法相同，但 PUT 要求在请求中提交所有信息',
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
    permission_classes = (IsSelfOrAdminOrReadOnly,)
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'


@swagger_auto_schema(
    method='PATCH',
    operation_summary='修改密码及邮箱',
    operation_description='1. 用户可以修改自己的密码及邮箱\n'
                          '2. 管理员还可以修改普通用户的密码及邮箱\n'
                          '3. 超级用户有权修改所有用户的密码及邮箱\n'
                          '为确保安全，修改者需要同时提交自身当前的密码（old_password 字段）\n\n'
                          '异常情况：'
                          '1. 若 id 不存在，返回 404\n'
                          '2. 若无权修改，返回 403 `{"detail": "没有权限修改"}`\n'
                          '3. 若自身密码错误，返回 403 `{"detail": "密码错误"}`\n'
                          '4. 若 new_password 不合法，返回 400 `{"detail": "新密码不合法"}`\n'
                          '5. 若 new_email 不合法，返回 400 `{"detail": "新邮箱不合法"}`\n'
                          '6. 若 new_email 已存在，返回 400 `{"detail": "新邮箱已存在"}`\n'
                          '验证正确性后，修改邮箱及密码，返回 204\n'
                          '注 1：new_email 和 new_password 可以不同时存在\n'
                          '注 2：若 new_email 和 new_password 其中一项错误，对另一项的修改也不会生效\n'
                          '注 3：修改密码会使得已有的登录失效，如果修改本人的',
    request_body=Schema_object(Schema_old_password, Schema_new_email, Schema_new_password),
    responses={200: Schema_None}
)
@api_view(['PATCH'])
@login_required
def change_password_view(request: Request, id: int) -> Response:
    user2 = get_object_or_404(User, id=id)
    # 权限判定
    if not hasGreaterPermissions(request.user, user2) and request.user != user2:
        return Response({"detail": "没有权限修改"}, status=status.HTTP_403_FORBIDDEN)
    if "old_password" not in request.data or \
            not authenticate(request, username=request.user.username, password=request.data["old_password"]):
        return Response({"detail": "密码错误"}, status=status.HTTP_403_FORBIDDEN)
    # 对更新数据合法性的判定
    new_email = request.data.pop('new_email', None)
    new_password = request.data.pop('new_password', None)
    if new_email:
        if not is_email(new_email):
            return Response({"detail": "新邮箱不合法"}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=new_email):
            return Response({"detail": "新邮箱已存在"}, status=status.HTTP_400_BAD_REQUEST)
    if new_password and not is_valid_password(new_password):
        return Response({"detail": "新密码不合法"}, status=status.HTTP_400_BAD_REQUEST)
    # 更新数据
    if new_email:
        user2.username = new_email
    if new_password:
        user2.set_password(new_password)
    user2.save()
    return Response(status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(
    method='GET',
    operation_summary='获取用户自身信息',
    operation_description='获取用户自身的信息，成功返回 200，应答和 `/users/<id>` 成功的应答相同\n'
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
