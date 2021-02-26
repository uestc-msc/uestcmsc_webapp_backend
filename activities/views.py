from django.utils.decorators import method_decorator
from django.utils.timezone import now
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters
from rest_framework.generics import *
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from activities.models import Activity
from activities.serializer import ActivitySerializer, ActivityAdminSerializer
from utils import *
from utils.permissions import *
from utils.swagger import *


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_summary='获取沙龙列表',
    operation_description='获取沙龙列表（以及总页数），可对标题、日期、时间、地点、演讲者姓名进行搜索，并可指定页码和每页大小\n'
                          '数据作为 list 返回在 `results` 中，返回值的 `count` 为搜索结果的总数\n'
                          '返回结果按日期时间降序排序\n'
                          '注：如页码不正确或不存在，返回 404\n'
                          '注：如每页大小不正确或不存在，使用默认每页大小（15）\n'
                          '注：如无搜索结果，返回 200，其中 `results` 为空\n',
                          # '注：需要登录，否则返回 403',
    manual_parameters=[Param_search, Param_page, Param_page_size],
))
@method_decorator(name='post', decorator=swagger_auto_schema(
    operation_summary='创建沙龙',
    operation_description='成功返回 201，参数错误返回 400\n'
                          '注：如果没有指明时区，datetime的输入输出默认使用东八区。\n'
                          '示例输入（以下输入均等价，输出 `2020-01-01T08:00:00+08:00`）：\n'
                          '`2020-01-01T00:00:00.000Z`\n'
                          '`2020-01-01T08:00:00.000+08:00`\n'
                          '`2020-01-01T08:00:00`\n'
                          '`2020-01-01T08:00`\n'
                          '`2020-01-01 08:00`\n'
                          '`2020-01-01 08:00+08:00`',
    request_body=Schema_object(Schema_title,
                               Schema_datetime,
                               Schema_location,
                               Schema_presenter_ids),
    responses={201: ActivitySerializer()}
))
class ActivityListView(ListCreateAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Activity.objects.all().order_by("-datetime")
    filter_backends = (filters.SearchFilter,)
    search_fields = ('title', 'datetime','location', 'presenter__first_name')
    pagination_class = Pagination
    serializer_class = ActivitySerializer


@method_decorator(name="get", decorator=swagger_auto_schema(
        operation_summary='获取沙龙信息',
        operation_description='获取沙龙信息\n'
))
@method_decorator(name="put", decorator=swagger_auto_schema(
    operation_summary='更新沙龙信息',
    operation_description='响应报文和 PATCH 方法相同，但 PUT 要求在请求中提交所有信息',
    request_body=Schema_object(Schema_title,
                               Schema_datetime,
                               Schema_location,
                               Schema_presenter_ids,
                               Schema_check_in_open),
    responses={201: ActivitySerializer()},
    ))
@method_decorator(name="patch", decorator=swagger_auto_schema(
    operation_summary='更新沙龙部分信息',
    operation_description='更新沙龙信息，成功返回 200\n'
                          '如沙龙不存在，返回 404\n'
                          '如更新值不合法，返回 400\n'
                          '注：更新参与者名单请使用 `/users/check_in/` 或 `/users/check_in_admin/` 接口\n'
                          '注：需要是沙龙演讲者或管理员，否则返回 403\n'
                          '注：PATCH 方法可以只提交更新的值，也可以提交所有值',
    request_body=Schema_object(Schema_title,
                               Schema_datetime,
                               Schema_location,
                               Schema_presenter_ids,
                               Schema_check_in_open),
    responses={201: ActivitySerializer()}
))
@method_decorator(name="delete", decorator=swagger_auto_schema(
    operation_summary='删除沙龙',
    operation_description='删除沙龙，成功返回 204\n'
                          '注：需要是沙龙演讲者或管理员，否则返回 403',
))
class ActivityDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsPresenterOrAdminOrReadOnly, )
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    lookup_field = 'id'


@method_decorator(name="get", decorator=swagger_auto_schema(
        operation_summary='获取沙龙额外信息（管理员）',
        operation_description='获取沙龙额外信息（如签到码）\n'
                              '注：需要是沙龙演讲者或管理员，否则返回 403',
))
class ActivityDetailAdminView(RetrieveAPIView):
    permission_classes = (IsPresenterOrAdmin, )
    queryset = Activity.objects.all()
    serializer_class = ActivityAdminSerializer
    lookup_field = 'id'


class ActivityCheckInView(GenericAPIView):
    permission_classes = (IsAuthenticated, )

    @swagger_auto_schema(
        operation_summary='用户签到',
        operation_description='可能会有以下情况：\n'
                              '1. 签到成功，用户经验+50，每位演讲者经验+10，返回 200'
                              '2. 已经签过到了，返回 200\n'
                              '2. 活动不存在，返回 404\n'
                              '3. POST 数据不包含签到码，返回 400\n'
                              '4. 非当日活动，返回 403\n'
                              '5. 演讲者关闭了签到，返回 403\n'
                              '6. 签到码错误，返回 403\n'
                              '注：要求登录，否则返回 403',
        request_body=Schema_object(Schema_check_in_code),
        responses={201: None, 403: Schema_object(Schema_detail)}
    )
    def post(self, request: WSGIRequest, id: int) -> Response:
        if not Activity.objects.filter(id=id):
            return Response({"detail": "活动不存在"}, status=status.HTTP_404_NOT_FOUND)
        activity = Activity.objects.get(id=id)
        if activity.attender.filter(id=request.user.id):
            return Response({"detail": "您已经签过到了"}, status=status.HTTP_200_OK)
        if not compare_date(activity.datetime, now()): #
            return Response({"detail": "非当日活动"}, status=status.HTTP_403_FORBIDDEN)
        if not activity.check_in_open:
            return Response({"detail": "演讲者已关闭签到"}, status=status.HTTP_403_FORBIDDEN)
        if "check_in_code" not in request.data:
            return Response({"detail": "POST 数据不包含签到码"}, status=status.HTTP_400_BAD_REQUEST)
        if request.data["check_in_code"] != activity.check_in_code:
            return Response({"detail": "签到码错误"}, status=status.HTTP_403_FORBIDDEN)
        activity.attender.add(request.user)
        # 经验系统：在做了在做了
        return Response({"detail": "签到成功，经验+50"}, status=status.HTTP_200_OK)


@method_decorator(name="patch", decorator=swagger_auto_schema(
    operation_summary='增量更新沙龙参与者名单',
    operation_description='更新沙龙参与者，成功返回 200\n'
                          '如更新的用户不存在，对请求不予执行，并返回 400\n'
                          '更新方法：将 add 中用户全部设为已签到，将 remove 中用户全部设为未签到\n'
                          '注：需要是管理员或沙龙演讲者，否则返回 403'
                          '注：该接口不受“演讲者关闭了签到”影响',
    request_body=Schema_object(Schema_add, Schema_remove),
    responses={200: ActivitySerializer()}
))
class ActivityAttenderUpdateView(GenericAPIView):
    permission_classes = (IsPresenterOrAdminOrReadOnly, )

    def patch(self, request: WSGIRequest, id: int) -> Response:
        if not Activity.objects.filter(id=id):
            return Response({"detail": "活动不存在"}, status=status.HTTP_404_NOT_FOUND)
        activity = Activity.objects.get(id=id)
        self.check_object_permissions(request, activity)

        add_list = request.data.pop('add', [])
        remove_list = request.data.pop('remove', [])
        add_user_list = list(User.objects.filter(id__in=add_list))
        remove_user_list = list(User.objects.filter(id__in=remove_list))
        if len(add_user_list) != len(add_list) or len(remove_user_list) != len(remove_list):    # 有 id 不存在
            return Response({"detail": "用户不存在"}, status=status.HTTP_400_BAD_REQUEST)
        activity.attender.add(*add_user_list)
        activity.attender.remove(*remove_user_list)

        return Response(ActivitySerializer(activity).data, status=status.HTTP_200_OK)
