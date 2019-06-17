from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from rest_framework.generics import RetrieveAPIView, CreateAPIView, UpdateAPIView, ListAPIView
from rest_framework.permissions import (AllowAny, IsAuthenticated, IsAdminUser)
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend


from aparnik.utils.utils import is_app_installed
from aparnik.packages.shops.files.api.serializers import FileListPolymorphicSerializer
from .serializers import BaseCourseListPolymorphicSerializer, BaseCourseDetailsPolymorphicSerializer, \
    CourseFileCreateSerializer, CourseCreateSerializer
from ..models import Course, CourseFile


def get_course(kwargs):
    return int(kwargs['course_id'])


def get_step(kwargs):
    return int(kwargs['step_id'])


class CourseListAPIView(ListAPIView):
    serializer_class = BaseCourseListPolymorphicSerializer
    permission_classes = [AllowAny]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ['description', 'title', ]
    filter_fields = ('publish_month', 'publish_week')

    def get_queryset(self):
        queryset = None
        user = self.request.user
        if any(name in self.request.query_params for name in ['search', 'publish_month', 'publish_week']):
            queryset = Course.objects.active(user)
        else:
            queryset = Course.objects.courses()

        if 'course_id' in self.request.parser_context['kwargs']:
            queryset = Course.objects.childs(course_obj=self.request.parser_context['kwargs']['course_id'])

        return queryset


class CourseUserListAPIView(ListAPIView):
    serializer_class = BaseCourseListPolymorphicSerializer
    permission_classes = [IsAuthenticated]
    # filter_backends = (filters.SearchFilter,)
    search_fields = ('id', 'publish_month', 'publish_week')

    def get_queryset(self):
        user = self.request.user
        queryset = Course.objects.active()
        if is_app_installed('aparnik.packages.shops.orders'):
            from aparnik.packages.shops.orders.models import Order
            queryset = Course.objects.filter(
                id__in=Order.objects.get_this_user_bought(user=user, custom_type=Course).values_list('items__product_obj', flat=True))
        return queryset


class CourseDetailAPIView(RetrieveAPIView):
    serializer_class = BaseCourseDetailsPolymorphicSerializer
    queryset = Course.objects.active()
    permission_classes = [AllowAny]
    lookup_url_kwarg = 'course_id'
    lookup_field = 'id'


class CourseCreateAPIView(CreateAPIView):
    serializer_class = CourseCreateSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        serializer.save()


# class StepOrderAPIView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def post(self, request, step_id, format=None, *args, **kwargs):
#         status = HTTP_400_BAD_REQUEST
#         user = self.request.user
#         id = step_id
#         content = {
#             'success': False,
#             'msg': '',
#             'data': {
#             },
#         }
#         order = None
#         step = None
#         try:
#             step = get_object_or_404(Step.objects.all(), id=id)
#         except Exception as e:
#             content["msg"] = e
#             content["success"] = False
#             content["data"] = {}
#             return Response(content, status=status)
#
#         try:
#             item = OrderItem.objects.get(product=step, order_obj__user=user, order_obj__status=Order.STATUS_COMPLETE)
#             order = item.order
#         except:
#             order = Order.objects.create(user=user)
#             item = order.add_item(product=step)
#             order.save()
#
#         content['data']['order'] = OrderSummarySerializer(order, many=False, read_only=True,
#                                                           context={'request': self.request}).data
#         content['success'] = True
#         status = HTTP_200_OK
#         return Response(content, status=status)

#
class CourseFileListAPIView(ListAPIView):
    # serializer_class = BaseCourseListPolymorphicSerializer
    serializer_class = FileListPolymorphicSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        serializer.save()

    # filter_backends = (filters.SearchFilter,)

    # def get_queryset(self, *args, **kwargs):
    #     return File.objects.filter(course_obj=self.kwargs['course_id']).order_by('sort')
    def get_queryset(self, *args, **kwargs):
        course = get_object_or_404(Course.objects.active(), id=self.request.parser_context['kwargs']['course_id'])
        return CourseFile.objects.active().filter(course_obj=course)


class CourseFileCreateAPIView(CreateAPIView):
    serializer_class = CourseFileCreateSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        serializer.save(course_obj_id=self.kwargs['course_id'])


class FileDownloadRequestAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, file_id, format=None, *args, **kwargs):
        status = HTTP_400_BAD_REQUEST
        user = self.request.user
        content = {
            'success': False,
            'msg': '',
            'data': {

            },
        }

        try:
            file = get_object_or_404(CourseFile.objects.get_this_user(user=user), id=file_id)

            key = self.request.data.get('key', None)
            if not key:
                content['msg'] += _('key is required')

            if content['msg']:
                raise ValidationError({'__all__': [_(content['msg'])]})

            (content["data"]["key"], content['data']['iv'], content["data"]["url_download"]) = file.get_key_url(
                user=user, key=key)
            content["data"]["url_download"] = self.request.build_absolute_uri(content["data"]["url_download"])
            content["success"] = True
            status = HTTP_200_OK

        except Exception as e:

            content["msg"] = e
            content["success"] = False
            content["data"] = {}
            status = HTTP_400_BAD_REQUEST

        return Response(content, status=status)
